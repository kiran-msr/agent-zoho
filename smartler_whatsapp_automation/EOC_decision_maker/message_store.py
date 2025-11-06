import json
import os
import re
from datetime import datetime


def save_group_messages(data, filename="groups.json"):
    """
    Save group messages to a file.
    - Keeps only today's data.
    - If the group already exists, append new messages.
    - If not, create a new entry.
    """
    today = datetime.now().strftime("%Y-%m-%d")

    # Load existing file if present
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                stored_data = json.load(f)
            except json.JSONDecodeError:
                stored_data = {"date": today, "groups": {}}
    else:
        stored_data = {"date": today, "groups": {}}

    # If stored date is not today, start fresh
    if stored_data.get("date") != today:
        stored_data = {"date": today, "groups": {}}

    groups_dict = stored_data["groups"]

    # Helper to remove ID in parentheses from group name
    def clean_group_name(name: str) -> str:
        return re.sub(r"\s*\([^)]*\)", "", name).strip()

    # Process incoming groups
    for group in data.get("groups", []):
        group_name = clean_group_name(group["groupName"])
        message = group["messages"].strip()

        if group_name in groups_dict:
            groups_dict[group_name] += "\n" + message
        else:
            groups_dict[group_name] = message

    # Save updated data
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(stored_data, f, ensure_ascii=False, indent=4)


def get_groupwise_messages(filename="groups.json") -> str:
    """
    Returns a string of today's group messages.
    - Blank string if no data found.
    - Format:
        Previous message of each groups in current day
            Group Name Message...
    """
    if not os.path.exists(filename):
        return ""  # blank if file missing

    with open(filename, "r", encoding="utf-8") as f:
        try:
            stored_data = json.load(f)
        except json.JSONDecodeError:
            return ""  # blank if corrupted

    groups = stored_data.get("groups", {})
    if not groups:
        return ""  # blank if no groups

    lines = ["Previous message of each groups in current day"]
    for group_name, messages in groups.items():
        # Combine group name and messages in a single indented line
        for msg_line in messages.split("\n"):
            lines.append(" " * 20 + f"{group_name} {msg_line}")

    return "\n".join(lines)

# -------- Example usage --------
if __name__ == "__main__":
    # Sample data
    sample_data = {
        "groups": [
            {
                "groupName": "ITV implementation - Taj Taal Kutir, Kolkata (120363357621473978@g.us)",
                "messages": "[12:00 AM, 08/05/2024] 120363357621473978: Now working fine"
            },
            {
                "groupName": "MSR Support - ITC Mughal (120363421152945450@g.us)",
                "messages": "[12:00 AM, 08/05/2024] 120363421152945450: "
            }
        ]
    }

    # Save messages (call this every 5 minutes in production)
    save_group_messages(sample_data)

    # Retrieve formatted messages
    print(get_groupwise_messages())

