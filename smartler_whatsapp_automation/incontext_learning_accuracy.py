
import json
import os, sys
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix

from google import genai
from google.genai import types
import base64

client = genai.Client(
    vertexai=True,
    project="whatsapp-zoho-ticket",
    location="us-central1"
)

model = "gemini-2.0-flash-001"
si_text = """You are an expert at analyzing conversations between multiple users. The users in this conversation are typically customers trying to resolve an issue with the help of service personnel. Given a sequence of chat messages followed by a target message, your task is to determine if the target message marks the end of a conversation or a continuation of the conversation thread. Your determination must be indicated by outputting 'end_of_conversation: true' for an end of conversation determination or 'end_of_conversation: false' otherwise."""
in_context_examples_text = """user44: Please update apk\nuser59: checking\n<target_message> user59: Living room or Bedroom??
end_of_conversation: false
user28: 3403 4602 vip room to check\nuser28: 3207 vip room to check\n<target_message> user19: 2204 tv not off in remote iPad guest room @~Sakthi check
end_of_conversation: true
user28: 3401 3407 vip room to check if\nuser28: 3301 3308 3311 vip room to check\n<target_message> user28: 4202 vip room to check
end_of_conversation: false
user31: It's working sir\n<target_message> user18: In #1714 only audio is playing
end_of_conversation: true
user28: 4702 vip room to check\nuser19: 2232 tv channels not forwarding @~Sakthi check\n<target_message> user39: Noted
end_of_conversation: false
user13: 524 up down button is not working\nuser59: calling\nuser45: Done\n<target_message> user13: Operator.... 311
end_of_conversation: true
"""

generate_content_config = types.GenerateContentConfig(
    temperature = 1,
    top_p = 0.95,
    max_output_tokens = 8192,
    system_instruction=[types.Part.from_text(text=si_text)]
)

ground_truths = []
predictions = []

with open('gemini_validation_data.jsonl', 'r') as f:
    for line in f:
        data = json.loads(line)
        system_instruction = data.get("systemInstruction")
        contents = data.get("contents")

        # Separate ground truth from the input
        ground_truth_text = None
        model_input = None
        for part in contents:
            if part.get('role') == 'model':
                ground_truth_text = part.get('parts', [{}])[0].get('text', '')
            else:
                model_input = types.Part.from_text(text=in_context_examples_text+part.get('parts')[0].get('text', ''))

        contents = [
            types.Content(
                role="user",
                parts=[model_input]
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
        
        predicted_value = 'true' in prediction_text
        ground_truth_value = 'true' in ground_truth_text

        predictions.append(predicted_value)
        ground_truths.append(ground_truth_value)
        
    # Calculate metrics
    accuracy = accuracy_score(ground_truths, predictions)
    f1 = f1_score(ground_truths, predictions)
    precision = precision_score(ground_truths, predictions)
    recall = recall_score(ground_truths, predictions)
    cm = confusion_matrix(ground_truths, predictions)

    print(f"Accuracy: {accuracy}")
    print(f"F1 Score: {f1}")
    print(f"Precision: {precision}")
    print(f"Recall: {recall}")
    print(f"Confusion Matrix:\n{cm}")

    tn, fp, fn, tp = cm.ravel()

    print("\n--- Confusion Matrix Explanation ---")
    print(f"True Negatives (TN): {tn} - The model correctly predicted 'end_of_conversation: false' when it was actually false.")
    print(f"False Positives (FP): {fp} - The model incorrectly predicted 'end_of_conversation: true' when it was actually false.")
    print(f"False Negatives (FN): {fn} - The model incorrectly predicted 'end_of_conversation: false' when it was actually true.")
    print(f"True Positives (TP): {tp} - The model correctly predicted 'end_of_conversation: true' when it was actually true.")
    print("------------------------------------")

