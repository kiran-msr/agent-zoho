import json
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix
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
"""


def create_client() -> genai.Client:
    """Initialize and return the genai client."""
    return genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)


def create_generate_config() -> types.GenerateContentConfig:
    """Return generation configuration with system instructions."""
    return types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        max_output_tokens=8192,
        system_instruction=[types.Part.from_text(text=SYSTEM_INSTRUCTION)],
    )


def extract_ground_truth_and_input(contents: list) -> tuple[str, types.Part]:
    """
    Separate ground-truth text from the model input.
    Returns (ground_truth_text, model_input_part).
    """
    ground_truth_text = ""
    model_input_part = None

    for part in contents:
        if part.get("role") == "model":
            ground_truth_text = part.get("parts", [{}])[0].get("text", "")
        else:
            user_text = part.get("parts", [{}])[0].get("text", "")
            model_input_part = types.Part.from_text(
                text=IN_CONTEXT_EXAMPLES + user_text
            )
    return ground_truth_text, model_input_part


def predict_end_of_conversation(client: genai.Client,
                                config: types.GenerateContentConfig,
                                model_input: types.Part) -> bool:
    """Call the model and return True if it predicts end_of_conversation: true."""
    contents = [types.Content(role="user", parts=[model_input])]
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=contents,
        config=config,
    )

    print("response: ",response)
    prediction_text = ""
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.text:
                prediction_text = part.text
    return "true" in prediction_text.lower()


def evaluate_model(file_path: str) -> None:
    """Run predictions, collect metrics, and print evaluation results."""
    client = create_client()
    config = create_generate_config()

    ground_truths, predictions = [], []

    with open(file_path, "r") as f:
        for line in f:
            data = json.loads(line)
            gt_text, model_input = extract_ground_truth_and_input(data.get("contents"))
            predicted = predict_end_of_conversation(client, config, model_input)
            predictions.append(predicted)
            ground_truths.append("true" in gt_text.lower())

    # Compute metrics
    accuracy = accuracy_score(ground_truths, predictions)
    f1 = f1_score(ground_truths, predictions)
    precision = precision_score(ground_truths, predictions)
    recall = recall_score(ground_truths, predictions)
    cm = confusion_matrix(ground_truths, predictions)

    print(f"Accuracy: {accuracy:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"Confusion Matrix:\n{cm}")

    tn, fp, fn, tp = cm.ravel()
    print("\n--- Confusion Matrix Explanation ---")
    print(f"True Negatives (TN): {tn} - Correctly predicted 'false'.")
    print(f"False Positives (FP): {fp} - Incorrectly predicted 'true' when false.")
    print(f"False Negatives (FN): {fn} - Incorrectly predicted 'false' when true.")
    print(f"True Positives (TP): {tp} - Correctly predicted 'true'.")
    print("------------------------------------")


if __name__ == "__main__":
    evaluate_model("gemini_validation_data.jsonl")

