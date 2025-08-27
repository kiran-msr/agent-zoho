"""
Main application manager.

This script is the main entry point of the application. It orchestrates the
workflow of getting the most recent message(s) from WhatsApp, finding the
corresponding contact(s) in Zoho Desk, and then creating new tickets in Zoho Desk.
"""
from whatsapp_agent_2 import get_whatsapp_agent, get_most_recent_message, WhatsappChat
from outlines_llm import get_outlines_llm
from zoho_client_secure import create_ticket, find_contact_by_field
import os
from dotenv import load_dotenv
from config import get_list_from_env
from datetime import datetime

print("executing task at ",datetime.now())
load_dotenv()

DEPARTMENT_ID = os.environ.get("ZOHO_DEPARTMENT_ID")
CONTACT_ID = os.environ.get("ZOHO_CONTACT_ID")
TEST_PHONE_NUMBER = "1 888 900 9646"
WHATSAPP_PHONE_NUMBER = "Test group"

#numbers = ["ITC Maurya - MSR Support"]
#numbers = ["120363402296086186@g.us","120363419133063958@g.us"]
numbers = get_list_from_env("WHATSAPP_GROUP_IDS")

#whatsapp_agent = get_whatsapp_agent()
#outlines_llm = get_outlines_llm()


def create_ticket_from_chat(chat: WhatsappChat, department_id: str) -> dict | None:
    """
    Creates a Zoho ticket from a WhatsappChat object.

    Args:
        chat (WhatsappChat): The WhatsApp chat message.
        department_id (str): The Zoho department ID.

    Returns:
        dict | None: The created ticket object if successful, otherwise None.
    """
    from_phone_number = chat.jid
   #message_body = chat.body
    #""" subject = chat.issue + " at " + chat.hotel_name + " in Room # " + chat.roomNo"""
    subject = chat.issue + " at Room # " + chat.roomNo
    room = chat.roomNo
    issuer = chat.last_sender
    hotelName = chat.hotel_name

    # Find Zoho contact
    zoho_contact = find_contact_by_field("phone", TEST_PHONE_NUMBER)
    if not zoho_contact:
        print(f"No Zoho contact found for {TEST_PHONE_NUMBER}")
        return None

    # Build ticket payload
    new_ticket_data = {
        "subject": subject,
        "departmentId": department_id,
        "contactId": zoho_contact["id"],
        "cf":{
                "cf_hotel_name":hotelName,
                "cf_room":room
            }

    }

    print(f"Creating a new ticket for {TEST_PHONE_NUMBER}...")
    created_ticket = create_ticket(new_ticket_data)

    if created_ticket:
        print("Ticket created successfully:", created_ticket)
    else:
        print(f"Failed to create ticket for {from_phone_number}")

    return created_ticket


def execute_task():
    whatsapp_agent = get_whatsapp_agent()
    outlines_llm = get_outlines_llm()

    chat_list = get_most_recent_message(numbers, whatsapp_agent, outlines_llm)

    # Create tickets for each chat
    for chat in chat_list.chats:
        create_ticket_from_chat(chat, DEPARTMENT_ID)



if __name__ == "__main__":
    # Get all most recent messages
    whatsapp_agent = get_whatsapp_agent()
    outlines_llm = get_outlines_llm()
    chat_list = get_most_recent_message(numbers, whatsapp_agent, outlines_llm)

    # Create tickets for each chat
    for chat in chat_list.chats:
        create_ticket_from_chat(chat, DEPARTMENT_ID)

