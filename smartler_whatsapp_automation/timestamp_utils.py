import os

from datetime import datetime

FILE_PATH = "timestamp.txt"

def save_timestamp(timestamp: datetime):
    """
    Save the given timestamp into a text file in ISO-8601 format.
    If the file already exists, overwrite it.
    """
    with open(FILE_PATH, "w") as file:
        file.write(timestamp.isoformat())

def read_timestamp() -> datetime | None:
    """
    Read the timestamp from the text file and return it as datetime.
    Returns None if file does not exist or is empty.
    """
    if not os.path.exists(FILE_PATH):
        return None

    with open(FILE_PATH, "r") as file:
        content = file.read().strip()
        return datetime.fromisoformat(content) if content else None




def save_two_timestamps(ts1: str, ts2: str):
    """
    Take two timestamps as input.
    Call save_timestamp() to store the first one.
    """
    # For now, just save the first timestamp
    save_timestamp(ts1)
    print(f"First timestamp saved: {ts1}")
