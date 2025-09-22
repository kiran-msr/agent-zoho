
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix
from google import genai
from google.genai import types

client = genai.Client(
    vertexai=True,
    project="641773534417",
    location="us-central1"
)

model = "projects/641773534417/locations/us-central1/endpoints/4341913143971151872"
si_text = """You are an expert at analyzing conversations between multiple users. The users in this conversation are typically customers trying to resolve an issue with the help of service personnel. Given a sequence of chat messages followed by a target message, your task is to determine if the target message marks the end of a conversation or a continuation of the conversation thread. Your determination must be indicated by outputting 'end_of_conversation: true' for an end of conversation determination or 'end_of_conversation: false' otherwise."""

generate_content_config = types.GenerateContentConfig(
    temperature = 1,
    top_p = 0.95,
    max_output_tokens = 8192,
    system_instruction=[types.Part.from_text(text=si_text)]
)

chat_message = """user26: Calling you,.no response,.please give me a call
user26: stb ip is not pinging in rn 524
<target_message> user46: Wtv not working this 10 time complaint I given till also same issue"""
print("="*80)
print(chat_message)
print("="*80)

contents = [
    types.Content(
        role="user",
        parts=[types.Part.from_text(text=chat_message)]
    )
]

response = client.models.generate_content(
            model = model,
            contents = contents,
            config = generate_content_config,
        )

for candidate in response.candidates:
    for part in candidate.content.parts:
        if part.text:
            prediction_text = part.text

print(prediction_text)