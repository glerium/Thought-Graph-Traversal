# **Request**
You are a professional X-ray results analyst. Please answer the following question about {organ} based on the image. Lest's think step by step.
# **Question**
{question}
# **Requirement**
- Respond a list in ​​JSON format​​, following the format in **Reply format**​​ structure.
- Do **not**​​ provide any irrelevant information. In the module of "reply" output **only** one sentence without any punctuation marks.
- **Reply Examples** provide some samples that you can use as a reference, and follow the style.
- Please display your thought process in the "think" module of the JSON.
- Let's think step by step in the "think" module of the JSON and output your thought with sentences.
# **Reply format**
{{
    "think": "your thought process",
    "reply": "your reply"
}}
# **Reply Examples**
{{
    "think": "{thought_examples[0]}",
    "reply": "{reply_examples[0]}"
}}

{{
    "think": "{thought_examples[1]}",
    "reply": "{reply_examples[1]}"
}}

{{
    "think": "{thought_examples[2]}",
    "reply": "{reply_examples[2]}"
}}
`