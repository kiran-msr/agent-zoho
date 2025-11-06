import re
import json
from pathlib import Path

MAPPING_FILE = Path("phone_user_map.json")


def load_mapping() -> dict:
    if MAPPING_FILE.exists():
        try:
            with open(MAPPING_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except json.JSONDecodeError:
            pass
    return {}


def save_mapping(mapping: dict):
    with open(MAPPING_FILE, "w") as f:
        json.dump(mapping, f, indent=2)


def remove_contact_info_keep_time(chat_text: str) -> str:
    """
    Works for all samples like:
        [10:08 AM, 24/09/2025 ] 918754596576: message
    Returns:
        [10:08 AM, 24/09/2025] user-<last5>: message
    """
    # Make sure literal '\n' in a single line become real newlines
    chat_text = chat_text.replace("\\n", "\n")

    mapping = load_mapping()

    # Capture the time/date and phone separately
    pattern = re.compile(
        r"(\[\d{1,2}:\d{2}\s*(?:AM|PM|am|pm),\s*\d{2}/\d{2}/\d{4}\s*\])\s*(\d+):\s*(.*)"
    )

    processed = []
    for line in chat_text.strip().splitlines():
        m = pattern.match(line.strip())
        if m:
            timestamp, phone_digits, message = m.groups()
            user_id = f"user-{phone_digits[-5:]}"
            if phone_digits not in mapping:
                mapping[phone_digits] = user_id
            processed.append(f"{timestamp} {mapping[phone_digits]}: {message}")
        else:
            # keep non-matching lines as-is
            processed.append(line.strip())

    save_mapping(mapping)
    return "\n".join(processed)


def remove_time_and_contact_info(chat_text: str) -> str:
    """
    Works for all samples like:
        [10:08 AM, 24/09/2025 ] 918754596576: message
    Returns:
        user-<last5>: message
    """
    # Make sure literal '\n' in a single line become real newlines
    chat_text = chat_text.replace("\\n", "\n")

    mapping = load_mapping()

    pattern = re.compile(
        r"\[\d{1,2}:\d{2}\s*(?:AM|PM|am|pm),\s*\d{2}/\d{2}/\d{4}\s*\]\s*(\d+):\s*(.*)"
    )

    processed = []
    for line in chat_text.strip().splitlines():
        m = pattern.match(line.strip())
        if m:
            phone_digits, message = m.groups()
            user_id = f"user-{phone_digits[-5:]}"
            if phone_digits not in mapping:
                mapping[phone_digits] = user_id
            processed.append(f"{mapping[phone_digits]}: {message}")
        else:
            # keep non-matching lines (e.g., “SAMPLE 1 …”) as-is
            processed.append(line.strip())

    save_mapping(mapping)
    return "\n".join(processed)


if __name__ == "__main__":
    sample_text = (
        "Sample 1 [10:08 AM, 24/09/2025 ] 918754596576: 3527 3507 vip room to check\\n"
        "[11:15 AM, 24/09/2025 ] 917598727010: Reached SAMPLE 3 "
        "[09:26 PM, 23/09/2025 ] 919846569358: Sure\\n"
        "[09:26 PM, 23/09/2025 ] 919846569358: Waiting for Oracle reply"
    )
    print(remove_time_and_contact_info(sample_text))

