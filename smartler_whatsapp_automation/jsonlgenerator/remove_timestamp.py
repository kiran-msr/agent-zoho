import json

def remove_timestamp(obj):
    if isinstance(obj, dict):
        # Create a new dictionary without the 'timestamp' key
        new_obj = {k: remove_timestamp(v) for k, v in obj.items() if k != 'timestamp'}
        return new_obj
    elif isinstance(obj, list):
        # Recursively process each item in the list
        return [remove_timestamp(elem) for elem in obj]
    else:
        # Return the object as is if it's not a dict or list
        return obj

def process_jsonl_file(input_file_path, output_file_path):
    with open(input_file_path, 'r') as infile, open(output_file_path, 'w') as outfile:
        for line in infile:
            try:
                json_data = json.loads(line)
                modified_data = remove_timestamp(json_data)
                outfile.write(json.dumps(modified_data) + '\n')
            except json.JSONDecodeError:
                print(f"Could not parse JSON: {line}")

if __name__ == "__main__":
    process_jsonl_file('1_extracted_data.jsonl', '2_no_timestamp.jsonl')
