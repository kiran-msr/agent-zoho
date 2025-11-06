import sys
from EOC_decision_maker.build_query import build_training_json
from EOC_decision_maker.incontext_learning_accuracy_3 import evaluate_conversations  # <-- import from your evaluation file
from EOC_decision_maker.remove_timestamp_and_phone_number import remove_contact_info_keep_time


# Example multi-line chat string
chat_text = """
user-64820: @~Sakthi check
user-32005: Noted
user-96576: 4306 vip room to check
user-32005: No issues found.
user-96576: 4101 vip room to check
user-96576: 4306 4101 3512 3515 vip room to check
user-96576: 3608 3601 vip room to check
user-70700: 3727 iPad not working
user-70700: Kenfix room please check
user-37797: Noted will check
"""

def run_eoc_decision_maker(chat_text):
    time_and_contact_removed_chat = remove_contact_info_keep_time(chat_text)
    result = process_chat(time_and_contact_removed_chat)
    return result


def process_chat(chat: str) -> str:
    """
    Build training data from a chat string, evaluate conversations,
    and return all predictions as a single formatted string.
    """
    training_data = build_training_json(chat)
    results = evaluate_conversations(training_data)

    lines = []
    for i, (item, pred) in enumerate(zip(training_data, results), start=1):
        target_msg = item["text"].split("<target_message>")[-1]
        lines.append(f" Target: {target_msg} => end_of_conversation: {pred}")

    return "\n".join(lines)

def main():
    output = process_chat(chat_text)
    print("\n=== End-of-Conversation Predictions ===")
    print(output)

if __name__ == "__main__":
    main()

