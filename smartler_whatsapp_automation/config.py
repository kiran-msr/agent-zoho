import os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

def get_list_from_env(var_name: str) -> list[str]:
    """
    Retrieve a comma-separated environment variable and return as list of strings.
    """
    value = os.getenv(var_name, "")
    return [item.strip() for item in value.split(",") if item.strip()]

