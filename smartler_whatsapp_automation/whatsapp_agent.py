from praisonaiagents import Agent, MCP
from outlines.models.openai import OpenAI
from pydantic import BaseModel
from typing import List 
from datetime import datetime,timedelta
from timestamp_utils import save_timestamp, read_timestamp
from datetime import timedelta
from config import get_list_from_env

class WhatsappChat(BaseModel):
    whatsapp_group_id: str
    jid: str
    whatsapp_group_name : str
    issue: str
    timestamp: str
    roomNo: str
    hotel_name: str
    last_sender: str

class WhatsappChatList(BaseModel):
    chats: List[WhatsappChat]


#last_timestamp = read_timestamp() 
#last_timestamp += timedelta(seconds=1)

def get_whatsapp_agent():
    """Gets the WhatsApp agent.

    This function initializes and returns a praisonai agent that is configured
    to interact with a WhatsApp MCP server.

    Returns:
        praisonaiagents.Agent: The WhatsApp agent.
    """
    whatsapp_agent = Agent(
        instructions="Whatsapp Agent",
        llm="gemini/gemini-2.0-flash",
        tools=MCP(
            command="/root/.local/bin/uv",
            args=["--directory","/usr/local/whatsapp-mcp/whatsapp-mcp-server","run","main.py"]
        ))
    return whatsapp_agent

"""
def join_phone_numbers(phone_numbers: list[str]) -> str:

    Joins phone numbers into a natural language string with 'and'.
    
    if not phone_numbers:
        return ""
    if len(phone_numbers) == 1:
        return phone_numbers[0]
    return ", ".join(phone_numbers[:-1]) + " and " + phone_numbers[-1]
"""

def join_phone_numbers(phone_numbers: list[str]) -> str:
    """
    Joins phone numbers into a string separated by commas.
    If only one number, returns it as-is.
    """
    return ", ".join(phone_numbers) if phone_numbers else ""

def filter_recent_chats(chat_list: WhatsappChatList, seconds: int = 30) -> WhatsappChatList:
    last_timestamp = read_timestamp() 
    last_timestamp += timedelta(seconds=1)
    """Filter chats based on timestamp freshness"""
    #print("chat_list print ",chat_list.chats)
    now = datetime.now()
    threshold = timedelta(seconds=seconds)
    retList = []
    for group_chat in chat_list.chats :
        #print("group_chat ",group_chat)
        if now - datetime.strptime(group_chat.timestamp, "%Y-%m-%d %H:%M:%S") <= threshold:
            retList.append(group_chat)
    return retList

def filter_chats_after_timestamp(chats: List[WhatsappChat], input_dt: datetime) -> WhatsappChatList:
    """Filter chats that have a timestamp later than the given input datetime.
       If a timestamp can't be parsed, skip that chat."""
    filtered = []

    for chat in chats.chats :
        try:
            chat_dt = datetime.strptime(chat.timestamp, "%Y-%m-%d %H:%M:%S")
            print("chat_dt ",chat_dt," ref time",input_dt)
            if chat_dt > input_dt:
                filtered.append(chat)
        except Exception:
            print("exception while prasing time")
            continue  # skip invalid timestamps
    print("filter list ",filtered)
    return WhatsappChatList(chats=filtered)


def get_most_recent_message(phone_numbers: list[str], whatsapp_agent: Agent, outlines_llm: OpenAI):

    last_timestamp = read_timestamp()
    last_timestamp += timedelta(seconds=1)
    """Gets the most recent message from a specific phone number.

    This function uses the WhatsApp agent to get the most recent message from a
    specific phone number. It then uses an outlines language model to extract
    structured data (JID, message body, and timestamp) from the agent's
    response.

    Args:
        phone_number (str): The phone number to get the most recent message from.
        whatsapp_agent (praisonaiagents.Agent): The WhatsApp agent.
        outlines_llm (outlines.models.openai.OpenAI): The outlines language model.

    Returns:
        tuple: A tuple containing the from_phone_number (str), message_body (str),
               and message_timestamp (str).
    """
    numbers_string = join_phone_numbers(phone_numbers)

    #message = outlines_llm(whatsapp_agent.start(f"get the most recent message in group(s) {numbers_string} and return it list of WhatsappChat class capture sender number also"), WhatsappChatList)
    #message = outlines_llm(whatsapp_agent.start(f"get the most recent message in group(s) {numbers_string} and return it list of WhatsappChat class capture sender number also. Get the hotel_name from chat group's name"), WhatsappChatList)
    #all_message = outlines_llm(whatsapp_agent.start(f"get the last 10 message in group(s) {numbers_string} and return it list of WhatsappChat class capture sender number and timestamp of format ISO 8601 with timezone offset also. Get the hotel_name from chat group's name"), WhatsappChatList)
    #all_message = outlines_llm(whatsapp_agent.start(f"get the last 10 message in group(s) {numbers_string} and return it list of WhatsappChat class after {last_timestamp}  capture sender number and timestamp also. Get the hotel_name from chat group's name"), WhatsappChatList)
    all_message = outlines_llm(whatsapp_agent.start(f"using configured whatsapp mcp tools get all messages in group(s) {numbers_string} and return it list of WhatsappChat class  after {last_timestamp}.  Capture sender number and timestamp also. Get the hotel_name from chat group's name. If no result found, return blank list.Don't give any example data"), WhatsappChatList)


    print("message all ", all_message)
    #message = filter_recent_chats(all_message, seconds=30)
    if len(all_message) > 0 :
        message_object = WhatsappChatList.model_validate_json(all_message)
        print("message_object print : ",message_object)
        #message_object = filter_recent_chats(message_object, seconds=600)
        #print("message ",message)

        message_object =  filter_chats_after_timestamp(message_object,last_timestamp)
        last_msg_time = None
        for group_chat in message_object.chats :
        #print("group_chat ",group_chat)
            currTime = datetime.strptime(group_chat.timestamp, "%Y-%m-%d %H:%M:%S")
            if last_msg_time is None or currTime > last_msg_time : 
                last_msg_time = currTime
        if last_msg_time is not None and last_msg_time > last_timestamp :
            save_timestamp(last_msg_time)

        print("message_object ",message_object)
        # from_phone_number = message_object.jid 
        # message_body = message_object.body
        # message_timestamp = message_object.timestamp
        # return from_phone_number, message_body, message_timestamp
        return message_object
    else :
        empty = []
        print("No new message in the last 30 secs")
        return empty

def test():
    from outlines_llm import get_outlines_llm
    whatsapp_agent = get_whatsapp_agent()
    outlines_llm = get_outlines_llm()
    #numbers = ["ITC Maurya - MSR Support","ITC Narmada Support"]
    #numbers = ["120363402296086186@g.us","120363419133063958@g.us"]
    numbers = get_list_from_env("WHATSAPP_GROUP_IDS")
    message_object = get_most_recent_message(numbers, whatsapp_agent, outlines_llm)
   # print(from_phone_number)
   # print(message_body)
   # print(message_timestamp)
   # print(message_object)


if __name__ == "__main__":
    test()







