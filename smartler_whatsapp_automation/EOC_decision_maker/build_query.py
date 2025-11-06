import json
from pathlib import Path

def build_training_json(chat_text: str):
    """
    Input: multi-line chat with user-IDs.
    Output: list of dicts:
       {
         "text": "<all previous lines>\n<target_message><current line>"
       }
    """
    lines = [l.strip() for l in chat_text.strip().splitlines() if l.strip()]
    output = []

    for i, line in enumerate(lines, start=1):
        context = "\n".join(lines[:i])                 # all lines up to current
        target = f"<target_message>{line}"
        output.append({"text": f"{context}\n{target}"})

    return output


if __name__ == "__main__":
    sample_text = """
    user-64820: @~Sakthi check
user-32005: Noted
user-96576: 4306 vip room to check
user-32005: No issues found.
user-96576: 4101 vip room to check
user-96576: 4306 4101 3512 3515 vip room to check
user-96576: 3608 3601 vip room to check
user-70700: 3727 iPad not working
user-70700: Kenfix room please check
user-37797: Noted will check"""
    
    result = build_training_json(sample_text)
    
    # Save to a file if desired
    out_file = Path("chat_training.json")
    out_file.write_text(json.dumps(result, indent=4), encoding="utf-8")
    
    # Print to console
    print(json.dumps(result, indent=4))

