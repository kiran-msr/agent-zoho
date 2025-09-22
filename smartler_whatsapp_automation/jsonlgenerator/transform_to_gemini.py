import json

def transform_data(input_file, output_file):
    system_instruction = {
        "role": "system",
        "parts": [
            {
                "text": "You are an expert at analyzing conversations between multiple users. The users in this conversation are typically customers trying to resolve an issue with the help of service personnel. Given a sequence of chat messages followed by a target message, your task is to determine if the target message marks the end of a conversation or a continuation of the conversation thread. Your determination must be indicated by outputting 'end_of_conversation: true' for an end of conversation determination  or 'end_of_conversation: false' otherwise."
            }
        ]
    }

    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            source_data = json.loads(line)
            
            contents = []
            
            user_texts = []
            # Process context messages
            for message in source_data.get("context", []):
                user_texts.append(f"{message['user']}: {message['text']}")
            
            # Process target message
            target_message = source_data.get("target_message")
            if target_message:
                user_texts.append(f"<target_message> {target_message['user']}: {target_message['text']}")

            contents.append({
                "role": "user",
                "parts": [
                    {
                        "text": "\n".join(user_texts)
                    }
                ]
            })
            
            # Process model output
            model_output = source_data.get("model")
            if model_output:
                contents.append({
                    "role": "model",
                    "parts": [
                        {
                            "text": f"end_of_conversation: {str(model_output['end_of_conversation']).lower()}"
                        }
                    ]
                })

            gemini_data = {
                "systemInstruction": system_instruction,
                "contents": contents
            }
            
            outfile.write(json.dumps(gemini_data) + '\n')

if __name__ == "__main__":
    transform_data('3_phone_to_userids.jsonl', 'gemini_finetuning_data.jsonl')