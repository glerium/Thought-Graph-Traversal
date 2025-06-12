# **Request**
You are a professional X-ray results analyst. Please write a brief sentence about the {organ} based on the two provided chest X-ray images.
# **Requirement**
- Respond a list in ​​JSON format​​, following the format in **Reply format**​​ structure.
- Do **not**​​ provide any irrelevant information. Output **only** one sentence without any punctuation marks
- If the {organ} show no abnormalities, simply output a normal report. If any anomalies are found, describe them in one sentence.
- **Reply Examples** provide some samples that you can use as a reference, and follow the style.
- Please display your thought process in the "think" module of the JSON.
- Let's think step by step in the "think" module of the JSON.
# **Reply format**
{{
    "think": "your thought process",
    "reply": "your reply"
}}
# **Reply Examples**
{{
    "think": "your thought process",
    "reply": "{reply_examples[0]}"
}}

{{
    "think": "your thought process",
    "reply": "{reply_examples[1]}"
}}

{{
    "think": "your thought process",
    "reply": "{reply_examples[2]}"
}}

{{
    "think": "your thought process",
    "reply": "{reply_examples[3]}"
}}

{{
    "think": "your thought process",
    "reply": "{reply_examples[4]}"
}}
