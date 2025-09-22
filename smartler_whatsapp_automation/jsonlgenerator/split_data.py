import json
import random
from collections import defaultdict

def get_eoc_value(item):
    for part in item.get('contents', []):
        if part.get('role') == 'model':
            text = part.get('parts', [{}])[0].get('text', '')
            if 'end_of_conversation: true' in text:
                return True
            if 'end_of_conversation: false' in text:
                return False
    return None

def split_data_stratified(input_file, training_file, validation_file, split_ratio=0.8):
    with open(input_file, 'r') as f:
        data = [json.loads(line) for line in f]

    # Stratify data based on 'end_of_conversation' value
    stratified_data = defaultdict(list)
    for item in data:
        eoc_value = get_eoc_value(item)
        if eoc_value is not None:
            stratified_data[eoc_value].append(item)

    training_data = []
    validation_data = []

    for eoc_value, items in stratified_data.items():
        random.shuffle(items)
        split_index = int(len(items) * split_ratio)
        training_data.extend(items[:split_index])
        validation_data.extend(items[split_index:])

    random.shuffle(training_data)
    random.shuffle(validation_data)

    with open(training_file, 'w') as f:
        for item in training_data:
            f.write(json.dumps(item) + '\n')

    with open(validation_file, 'w') as f:
        for item in validation_data:
            f.write(json.dumps(item) + '\n')

if __name__ == "__main__":
    split_data_stratified(
        'gemini_finetuning_data.jsonl',
        'gemini_post_training_data.jsonl',
        'gemini_validation_data.jsonl'
    )