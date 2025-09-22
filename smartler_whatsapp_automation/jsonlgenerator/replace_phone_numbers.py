import json

def find_phone_numbers(obj, phone_numbers):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == 'sender':
                phone_numbers.add(v)
            else:
                find_phone_numbers(v, phone_numbers)
    elif isinstance(obj, list):
        for elem in obj:
            find_phone_numbers(elem, phone_numbers)

def replace_fields(obj, phone_number_to_user_id):
    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            if k == 'sender' and v in phone_number_to_user_id:
                new_obj['user'] = phone_number_to_user_id[v]
            elif k == 'label':
                new_obj['model'] = {"end_of_conversation": True if v == 1 else False}
            else:
                new_obj[k] = replace_fields(v, phone_number_to_user_id)
        return new_obj
    elif isinstance(obj, list):
        return [replace_fields(elem, phone_number_to_user_id) for elem in obj]
    else:
        return obj

def process_data(input_file_path, output_file_path, user_id_map_path):
    phone_numbers = set()
    with open(input_file_path, 'r') as infile:
        for line in infile:
            try:
                json_data = json.loads(line)
                find_phone_numbers(json_data, phone_numbers)
            except json.JSONDecodeError:
                print(f"Could not parse JSON: {line}")

    phone_number_to_user_id = {phone: f'user{i+1}' for i, phone in enumerate(phone_numbers)}

    with open(user_id_map_path, 'w') as map_file:
        json.dump(phone_number_to_user_id, map_file, indent=2)

    with open(input_file_path, 'r') as infile, open(output_file_path, 'w') as outfile:
        for line in infile:
            try:
                json_data = json.loads(line)
                modified_data = replace_fields(json_data, phone_number_to_user_id)
                outfile.write(json.dumps(modified_data) + '\n')
            except json.JSONDecodeError:
                print(f"Could not parse JSON: {line}")

if __name__ == "__main__":
    process_data('2_no_timestamp.jsonl', '3_phone_to_userids.jsonl', '4_phone_userid_map.json')
