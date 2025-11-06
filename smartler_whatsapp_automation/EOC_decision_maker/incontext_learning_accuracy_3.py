import json
from google import genai
from google.genai import types

MODEL_NAME = "gemini-2.0-flash-001"
PROJECT_ID = "whatsapp-zoho-ticket"
LOCATION = "us-central1"

SYSTEM_INSTRUCTION = (
    "You are an expert at analyzing conversations between multiple users. "
    "The users in this conversation are typically customers trying to resolve an issue with the help of service personnel. "
    "Given a sequence of chat messages followed by a target message, your task is to determine if the target message marks "
    "the end of a conversation or a continuation of the conversation thread. "
    "Your determination must be indicated by outputting 'end_of_conversation: true' for an end of conversation determination "
    "or 'end_of_conversation: false' otherwise."
)

IN_CONTEXT_EXAMPLES = """user44: Please update apk
user59: checking
<target_message> user59: Living room or Bedroom??
end_of_conversation: false
user28: 3403 4602 vip room to check
user28: 3207 vip room to check
<target_message> user19: 2204 tv not off in remote iPad guest room @~Sakthi check
end_of_conversation: true
user28: 3401 3407 vip room to check if
user28: 3301 3308 3311 vip room to check
<target_message> user28: 4202 vip room to check
end_of_conversation: false
user31: It's working sir
<target_message> user18: In #1714 only audio is playing
end_of_conversation: true
user28: 4702 vip room to check
user19: 2232 tv channels not forwarding @~Sakthi check
<target_message> user39: Noted
end_of_conversation: false
user13: 524 up down button is not working
user59: calling
user45: Done
<target_message> user13: Operator.... 311
end_of_conversation: true
user21: The Chamber Gateway IP - 172.16.0.1 -- mac id 00:e0:4c:68:26:db\nThe Inner Circle Gateway IP - 10.1.0.25 --- mac id 00:e0:4c:68:2a:54\nuser21: @~Harisudhan ji\nuser35: Now pls check whether you were able to reach the ip's from casting server.\nuser21: ok\nuser21: it's not pining\n<target_message> user48: Support Desk Roster for week beginning 31st August 2025
end_of_conversation: true
user41: Noted\n<target_message> user20: 547 tv apps volume is locked
end_of_conversation: true
user5: Living romm tv\nuser5: Tv power issue 1802\n<target_message> user49: 1408 Mr. Rodenbeck (German delegation) mentioned upon checkout that the television in the room wasn’t working. Kindly have it checked please.
end_of_conversation: true
user59: Please check the wallpaper, this is not our property\nuser47: Noted sir\n<target_message> user47: @+91 98300 44553 as discussed, please update images as soon as possible
end_of_conversation: true
user27: room: 2014 || AC control issue , someone please update on this open ticket\n<target_message> user27: Someone please respond
end_of_conversation: true
user3: Sir can you please clear the data and check once\nuser47: Same\n<target_message> user3: Sir as we discussed the images is changed and correct image is reflecting
end_of_conversation: true
user53: @~... as we discussed please check all the services and update\nuser53: Services was up and running fine. Live ip was down due to isp issue. Now we are able to access vm and portal.\n<target_message> user16: Kindly  do test check  in room 1228
end_of_conversation: true
"""

def create_client() -> genai.Client:
    return genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

def create_generate_config() -> types.GenerateContentConfig:
    return types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        max_output_tokens=1024,
        system_instruction=[types.Part.from_text(text=SYSTEM_INSTRUCTION)],
    )

def predict_end_of_conversation(client: genai.Client,
                                config: types.GenerateContentConfig,
                                conversation_text: str) -> bool:
    """Send a single conversation to Gemini and return True if model predicts end_of_conversation: true."""
    full_prompt = IN_CONTEXT_EXAMPLES + conversation_text
    contents = [types.Content(role="user", parts=[types.Part.from_text(text=full_prompt)])]
    response = client.models.generate_content(model=MODEL_NAME, contents=contents, config=config)

    prediction_text = ""
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.text:
                prediction_text += part.text

    return "true" in prediction_text.lower()

def evaluate_conversations(conversations: list[dict]) -> list[bool]:
    """Takes a list of dicts with a 'text' key and returns a list of True/False predictions."""
    client = create_client()
    config = create_generate_config()

    results = []
    for item in conversations:
        conv_text = item.get("text", "")
        is_end = predict_end_of_conversation(client, config, conv_text)
        results.append(is_end)
    return results

# Example usage:
if __name__ == "__main__":
    data = [
        {"text": "user-64820: @~Sakthi check\n<target_message>user-64820: @~Sakthi check"},
        {"text": "user-64820: @~Sakthi check\nuser-32005: Noted\n<target_message>user-32005: Noted"},
        # ... rest of your items
    ]
    predictions = evaluate_conversations(data)
    for i, pred in enumerate(predictions, 1):
        print(f"Conversation {i}: end_of_conversation = {pred}")

