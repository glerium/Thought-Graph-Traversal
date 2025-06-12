# **Request**
You are a doctor skilled in analyzing X-rays. Please determine whether the following question-answer pair is consistent with X-ray imaging. (Current time: {datetime})
# **Question**
{question}
# **Answer**
{answer}
# **Requirement**
- Please return the results in JSON format without any extraneous output.
- Please follow the format of the Reply Format.
- If the answer matches the X-ray image, please return true in the JSON; otherwise, return false.
# **Reply Format**
{{
    "is_correct":
}}
# **Reply Examples**
## **Examples 1** (matches the X-ray image)
{{
    "is_correct": true
}}
## **Examples 2** (does not match the X-ray image)
{{
    "is_correct": false
}}