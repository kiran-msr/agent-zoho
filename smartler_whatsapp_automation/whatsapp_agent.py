from praisonaiagents import Agent, MCP
from outlines.models.openai import OpenAI
from pydantic import BaseModel
from typing import List 

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



def get_most_recent_message(phone_numbers: list[str], whatsapp_agent: Agent, outlines_llm: OpenAI):
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

    message = outlines_llm(whatsapp_agent.start(f"get the most recent message in group(s) {numbers_string} and return it list of WhatsappChat class capture sender number also"), WhatsappChatList)
    message_object = WhatsappChatList.model_validate_json(message)
    print("message ",message)
    print("message_object ",message_object)
    # from_phone_number = message_object.jid 
    # message_body = message_object.body
    # message_timestamp = message_object.timestamp
    # return from_phone_number, message_body, message_timestamp
    return message_object

def test():
    from outlines_llm import get_outlines_llm
    whatsapp_agent = get_whatsapp_agent()
    outlines_llm = get_outlines_llm()
    numbers = ["Troubleshooting Group"]
    message_object = get_most_recent_message(numbers, whatsapp_agent, outlines_llm)
   # print(from_phone_number)
   # print(message_body)
   # print(message_timestamp)
    print(message_object)


if __name__ == "__main__":
    test()

