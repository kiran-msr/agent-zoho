"""
A Python client for the Zoho Desk API.

This script provides a client for interacting with the Zoho Desk API. It handles
authentication using OAuth2 with a refresh token, and provides functions for
getting and creating tickets.

The script reads all necessary credentials and configuration from environment
variables, which can be stored in a .env file.
"""
import requests
import time
import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

# Load credentials from environment variables
REFRESH_TOKEN = os.environ.get("ZOHO_REFRESH_TOKEN")
CLIENT_ID = os.environ.get("ZOHO_CLIENT_ID")
CLIENT_SECRET = os.environ.get("ZOHO_CLIENT_SECRET")
ORG_ID = os.environ.get("ZOHO_ORG_ID")
DEPARTMENT_ID = os.environ.get("ZOHO_DEPARTMENT_ID")
CONTACT_ID = os.environ.get("ZOHO_CONTACT_ID")
ZOHO_BASE_URL = os.environ.get("ZOHO_BASE_URL")
ZOHO_TOKEN_URL = os.environ.get("ZOHO_TOKEN_URL")
ZOHO_SCOPE = os.environ.get("ZOHO_SCOPE")
ZOHO_ACCESS_TOKEN = os.environ.get("ZOHO_ACCESS_TOKEN")


# Check if all required environment variables are set
if not all([REFRESH_TOKEN, CLIENT_ID, CLIENT_SECRET, ORG_ID, DEPARTMENT_ID, CONTACT_ID, ZOHO_BASE_URL, ZOHO_TOKEN_URL, ZOHO_SCOPE]):
    print("Error: Please set all required environment variables.")
    print("Required variables: ZOHO_REFRESH_TOKEN, ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET, ZOHO_ORG_ID, ZOHO_DEPARTMENT_ID, ZOHO_CONTACT_ID, ZOHO_BASE_URL, ZOHO_TOKEN_URL, ZOHO_SCOPE")
    exit()

# Global variables to store the token and its expiry time
access_token = None
token_expires_at = 0

class Contact(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    secondary_email: str
    account_name: str
    contact_owner: str
    ownerId: int
    phone: str
    mobile: str
    type: str
    title: str

def refresh_access_token():
    """Refreshes the access token using the refresh token.

    This function makes a POST request to the Zoho token endpoint to get a new
    access token. It then stores the new token and its expiry time in global
    variables.
    """
    global access_token, token_expires_at
    print("Refreshing access token...")
    try:
        data = {
            "refresh_token": REFRESH_TOKEN,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "scope": ZOHO_SCOPE,
            "grant_type": "refresh_token",
        }
        response = requests.post(ZOHO_TOKEN_URL, data=data)
        response.raise_for_status()
        token_data = response.json()
        access_token = token_data["access_token"]
        # expires_in is in seconds, so we calculate the expiry timestamp
        token_expires_at = time.time() + token_data.get("expires_in", 3600) # Default to 1 hour
        print(f"Access token refreshed successfully: {access_token}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while refreshing the token: {e}")
        access_token = None

def get_access_token():
    """Gets a valid access token.

    This function checks if the current access token is expired. If it is, it
    calls the refresh_access_token() function to get a new one.

    Returns:
        str: A valid access token.
    """
  #  global access_token, token_expires_at
  #  if not access_token or time.time() >= token_expires_at:
  #      refresh_access_token()
  #  return access_token 
    return ZOHO_ACCESS_TOKEN

def get_headers():
    """Gets the headers for an API request.

    This function gets a valid access token and constructs the necessary headers
    for making a request to the Zoho Desk API.

    Returns:
        dict: A dictionary of headers.
    """
    token = get_access_token()
    if not token:
        raise Exception("Could not retrieve access token.")
    return {
        "orgId": ORG_ID,
        "Authorization": f"Zoho-oauthtoken {token}",
    }

def get_tickets():
    """Gets all tickets from the Zoho Desk API.

    This function makes a GET request to the /tickets endpoint to retrieve all
    tickets.

    Returns:
        dict: A dictionary containing the API response, or None if an error
              occurred.
    """
    try:
        headers = get_headers()
        response = requests.get(f"{ZOHO_BASE_URL}/tickets", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def get_contacts():
    """Gets all contacts from the Zoho Desk API.

    This function makes a GET request to the /contacts endpoint to retrieve all
    contacts.

    Returns:
        dict: A dictionary containing the API response, or None if an error
              occurred.
    """
    try:
        headers = get_headers()
        response = requests.get(f"{ZOHO_BASE_URL}/contacts", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def create_ticket(ticket_data):
    """Creates a new ticket in the Zoho Desk API.

    This function makes a POST request to the /tickets endpoint to create a new
    ticket.

    Args:
        ticket_data (dict): A dictionary containing the data for the new ticket.

    Returns:
        dict: A dictionary containing the API response, or None if an error
              occurred.
    """
    try:
        headers = get_headers()
        response = requests.post(f"{ZOHO_BASE_URL}/tickets", json=ticket_data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def find_contact_by_field(field_name, field_value):
    """Finds a contact by a specific field value.

    This function gets all contacts and loops through them to find a contact
    with a specific field value.

    Note: This function currently only searches the first page of contacts.
          For a complete solution, pagination needs to be implemented in the
          get_contacts() function.

    Args:
        field_name (str): The name of the field to search in.
        field_value (str): The value to search for.

    Returns:
        dict: The contact dictionary if a match is found, or None otherwise.
    """
    print(f"Searching for contact with {field_name} = {field_value}...")
    contacts_response = get_contacts()
    if contacts_response and "data" in contacts_response:
        for contact in contacts_response["data"]:
            if field_name in contact and contact[field_name] == field_value:
                return contact
    return None

def test():
    # Example usage:
    for count in range(4):
        new_ticket_data = {
            "subject": f"Minimal Test Ticket {count}",
            "departmentId": DEPARTMENT_ID,
            "contactId": CONTACT_ID,
        }
        print("Creating a new ticket...")
        created_ticket = create_ticket(new_ticket_data)
        if created_ticket:
            print("Ticket created successfully:", created_ticket)
        print("------------------------")

    print("=========================================================")
    print("\nGetting all tickets...")
    all_tickets = get_tickets()
    if all_tickets:
        print("All tickets:", all_tickets)

    print("=========================================================")
    print("\nGetting all contacts...")
    all_contacts = get_contacts()
    if all_contacts:
        print("All contacts:", all_contacts)

    print("=========================================================")
    # Example of finding a contact by phone number
    phone_number_to_find = "4044832145" # Replace with a real phone number from your contacts
    found_contact = find_contact_by_field("phone", phone_number_to_find)
    if found_contact:
        print(f"Found contact: {found_contact}")
    else:
        print(f"Could not find contact with phone number {phone_number_to_find}")

if __name__ == "__main__":
    test()
