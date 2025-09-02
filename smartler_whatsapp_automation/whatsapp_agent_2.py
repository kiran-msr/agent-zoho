from praisonaiagents import Agent, MCP
from outlines.models.openai import OpenAI
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
from dateutil import parser
from timestamp_utils import save_timestamp, read_timestamp
from config import get_list_from_env
from config import get_list_from_env_with_delim
from dotenv import load_dotenv
import os

load_dotenv()
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY", "")
# -------------------------------
# Models
# -------------------------------
class WhatsappChat(BaseModel):
    whatsapp_group_id: str
    jid: str
    whatsapp_group_name: str
    issue: str
    timestamp: datetime   # Pydantic will auto-parse many formats
    roomNo: str
    hotel_name: str
    last_sender: str

    def normalized(self):
        """Return a normalized dict with timestamp in '%Y-%m-%d %H:%M:%S'"""
        return {
            **self.dict(exclude={"timestamp"}),
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }


class WhatsappChatList(BaseModel):
    chats: List[WhatsappChat]


# -------------------------------
# Agent setup
# -------------------------------
def get_whatsapp_agent():
    os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY", "")
    """Initialize the WhatsApp agent with MCP server."""
    whatsapp_agent = Agent(
        instructions="Whatsapp Agent",
        llm="gemini/gemini-2.0-flash",
        tools=MCP(
            command="/root/.local/bin/uv",
            args=[
                "--directory",
                "/usr/local/agent-zoho/whatsapp-mcp/whatsapp-mcp-server",
                "run",
                "main.py"
            ]
        )
    )
    return whatsapp_agent


# -------------------------------
# Utils
# -------------------------------
def join_string(data: list[str]) -> str:
    return ", ".join(data) if data else ""


def filter_chats_after_timestamp(chats: WhatsappChatList, input_dt: datetime) -> WhatsappChatList:
    """Keep only chats with timestamp after given datetime."""
    filtered = []
    for chat in chats.chats:
        try:
            if chat.timestamp > input_dt:
                print("chat time ",chat.timestamp," ref time ",input_dt)
                filtered.append(chat)
        except Exception as e:
            print("⚠️ Skipping chat due to timestamp parse error:", e)
            continue
    return WhatsappChatList(chats=filtered)

def get_whatsapp_group_info(whatsapp_agent: Agent,group_names: list[str]):
    group_names = join_string(group_names)
    raw_response = whatsapp_agent.start(
        f"get the group whatsapp id of group names {group_names} . consider the following points in mind.   1) search it all at once. 2) return the info in json format. 3) don't ask me for further search, search all the items at once."
    )
    print(" response ",raw_response)



# -------------------------------
# Core function
# -------------------------------
def get_most_recent_message(phone_numbers: list[str], whatsapp_agent: Agent, outlines_llm: OpenAI):
    last_timestamp = read_timestamp() + timedelta(seconds=1)
    numbers_string = join_string(phone_numbers)

    # 1) Call MCP tool explicitly (just fetch raw messages)
    print(f"📡 Calling MCP server for groups {numbers_string} after {last_timestamp}")
    raw_response = whatsapp_agent.start(
        f"get all messages in group(s) {numbers_string} after {last_timestamp} along with group name"
    )
    print("✅ MCP server raw response:", raw_response)

    print(f"📡 Calling MCP server for groups {numbers_string} after {last_timestamp}")
    raw_response = whatsapp_agent.start(
            f"group the messages based on sender and order the messages of each sender in ascending time order .Raw messages: {raw_response} "
    )
    print("✅ MCP server raw response:", raw_response)

    #raw_response = whatsapp_agent.start(
    #        f"filter out all the messages before {last_timestamp} .Raw messages: {raw_response} "
    #)
    #print("✅ MCP server raw response:", raw_response)

    if not raw_response or raw_response.strip() == "":
        print("⚠️ MCP server returned nothing")
        return WhatsappChatList(chats=[])

    # 2) Structure with Outlines LLM (now carries extraction instructions)
    structured_response = outlines_llm(
        f"""You are a JSON generator.
Respond ONLY with valid JSON conforming exactly to the schema below.
Do not include explanations, clarifications, or examples.
If no messages with actionable issues are found, return {{"chats": []}}.

Goal:
Analyze the Raw MCP data (below) and extract reported operational issues per room per WhatsApp group.
Each output object must represent one consolidated issue for a specific room in a specific group.

Rules (follow exactly):
1) hotel_name: extract from whatsapp_group_name — use the substring before the first " - ", "|" or ":"; if none, use the full group name. ignore word "MSR", "Support" if present. 
2) roomNo: detect explicit room numbers from message text using patterns like "room 5262", "rm 5262", "roomNo: 438", "room#438" or standalone 2-5 digit sequences that appear near the word "room", "rm", "roomno", or "guest". If no reliable room number is found, set roomNo to "". If there are multiple occurance of room numbers in single message, break it into separate individual message for each room with same mentioned issue or context.
3) Aggregation: if multiple messages refer to the same problem for the same room in the same group, MERGE them into one WhatsappChat object. The merged "issue" must be a single concise sentence (no quotes), summarizing the problem or request (max 30 words). Keep only the core actionable symptom or request; omit greetings and filler.
4) timestamp: use the timestamp of the LATEST message included in the aggregated issue.Output it as a string formatted exactly "%Y-%m-%d %H:%M:%S" (no timezone suffix)(e.g. 2025-01-05 13:42:25) . If parsing/conversion fails, set timestamp to "". All timestamp in chats are in Asia/Kolkata timezone , no need to covert timezones.
5) last_sender: telephone number of the sender of the latest message in the aggregated issue. If unavailable, use "".
6) whatsapp_group_id and jid: set both to the group's JID as present in raw data. whatsapp_group_name: use the raw group name.
7) issue filtering: ignore irrelevant messages (greetings, acknowledgements, emojis, "ok", "thanks", chit-chat, repeated confirmations). Only extract actionable problem descriptions or requests. System/admin messages should only be used if they contain actual issue text.
8) Multiple distinct issues or different room numbers => produce separate WhatsappChat entries.
9) Output must strictly match the schema below. Do not add, rename, or remove fields. Use empty strings ("") for missing textual fields and return an empty list ({{"chats": []}}) when no issues found.
10) Conservative behavior: if you cannot confidently identify a room or an actionable issue from messages, skip that message.

Schema:
class WhatsappChat(BaseModel):
    whatsapp_group_id: str
    jid: str
    whatsapp_group_name: str
    issue: str
    timestamp: str
    roomNo: str
    hotel_name: str
    last_sender: str

class WhatsappChatList(BaseModel):
    chats: List[WhatsappChat]

Raw MCP data:
{raw_response}

""",
        WhatsappChatList
    )

    print("📥 Structured response:", structured_response)

    # 3) Parse & normalize
    message_object = WhatsappChatList.model_validate_json(structured_response)

    # Filter out old chats
    message_object = filter_chats_after_timestamp(message_object, last_timestamp)

    last_msg_time = None
    for group_chat in message_object.chats :
    #print("group_chat ",group_chat)
        currTime = group_chat.timestamp
        if last_msg_time is None or currTime > last_msg_time : 
            last_msg_time = currTime
    if last_msg_time is not None and last_msg_time > last_timestamp :
        save_timestamp(last_msg_time)


    # Save latest timestamp
    #if message_object.chats:
    #    last_msg_time = max(chat.timestamp for chat in message_object.chats)
    #    if last_msg_time > last_timestamp:
    #        save_timestamp(last_msg_time)

    # Return normalized output
    #normalized_chats = [WhatsappChat(**chat.normalized()) for chat in message_object.chats]
    #return WhatsappChatList(chats=normalized_chats)
    return message_object

# -------------------------------
# Test runner
# -------------------------------
def test():
    from outlines_llm import get_outlines_llm
    whatsapp_agent = get_whatsapp_agent()
    outlines_llm = get_outlines_llm()
    numbers = get_list_from_env("WHATSAPP_GROUP_IDS")
    print("numbers ",numbers)
    message_object = get_most_recent_message(numbers, whatsapp_agent, outlines_llm)
    print("🎯 Final normalized message object:", message_object)


def test2():
    group_names = get_list_from_env_with_delim("WHATSAPP_GROUP_NAMES","|")
    whatsapp_agent = get_whatsapp_agent()
    get_whatsapp_group_info(whatsapp_agent,group_names)

if __name__ == "__main__":
    test2()

