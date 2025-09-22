import json

def extract_senders(jsonl_path: str):
    senders = set()
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)
            # Collect senders from context
            for ctx in data.get("context", []):
                if "sender" in ctx:
                    senders.add(ctx["sender"])
            # Collect sender from target_message
            target = data.get("target_message", {})
            if "sender" in target:
                senders.add(target["sender"])
    return senders

if __name__ == "__main__":
    input_file = "1_extracted_data.jsonl"      # replace with your JSONL filename
    output_file = "4_phone_userid_map.json"    # output mapping file

    # Extract all unique phone numbers
    all_senders = sorted(extract_senders(input_file))

    # Create mapping: phone number -> userX
    phone_user_map = {phone: f"user{i+1}" for i, phone in enumerate(all_senders)}

    # Save to JSON file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(phone_user_map, f, indent=2)

    print(f"Mapping saved to {output_file}")

