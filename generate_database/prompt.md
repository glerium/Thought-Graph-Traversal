# **Request**
You are an assistant responsible for performing simple tasks. Please analyze each sentence in the report one by one to determine if it describes any organ from the list. If found, record the sentence number(s) in the format shown in the **Example**. If an organ not described in the List appears in the sentence, please add the corresponding organ in your response.
# **Report**
{report}
# **List**
{organ_list}
# **Requirement**
- Please return the results in JSON format without any extraneous output.
- If an organ not described in the **List** appears in the sentence, please add the corresponding organ in your response.
- If descriptions of the organ appear in multiple sentences, return multiple numbers as shown in the **Example**.
- **Only** return the sentence numbers (e.g., 1, 2, etc.) where each organ in the list is mentioned.
- If an organ is not mentioned, follow the **Example** format for such cases.
- Sentences are delimited by periods ('.'), for example: '1st sentence . 2nd sentence . 3rd sentence . 4th sentence'.
# **Reply format**
{{
    "sentence": {{
        "1st": [],
        "2nd": [],
        "3rd": [],
        "4th": [],
        "5th": [],
        "6th": [],
        "7th": [],
        "8th": [],
        "9th": [],
        "10th": [],
        "11th": [],
        "12th": [],
        "13th": [],
        "14th": [],
        "15th": []
    }},
    "list": {format_organ_list}
    
}}
# **Reply Example**
## Report
the cardiomediastinal silhouette is normal size and configuration . pulmonary vasculature within normal limits . the heart and lungs are clear . the heart size is in noraml limit . bony structures are intact .
## Reply
{{
    "sentence": {{
        "1st": ["the cardiomediastinal silhouette is normal size and configuration"],
        "2nd": ["pulmonary vasculature within normal limits"],
        "3rd": ["the heart and lungs are clear"],
        "4th": ["the heart size is in noraml limit"],
        "5th": ["bony structures are intact"],
        "6th": [],
        "7th": [],
        "8th": [],
        "9th": [],
        "10th": [],
        "11th": [],
        "12th": [],
        "13th": [],
        "14th": [],
        "15th": []
    }},
    "list": {{
        "cardiomediastinal silhouette": [1],
        "heart": [3, 4],
        "lungs": [3],
        "pneumothorax": [],
        "pleural effusion": [],
        "bones": [5]
    }}
}}
## Explaination
the first sentence is 'the cardiomediastinal silhouette is normal size and configuration', which discribes about "cardiomediastinal silhouette" in the List.
the second sentence is 'pulmonary vasculature within normal limits', which discribes nothing contained in the List.
the third sentence is 'the heart and lungs are clear', which discribes about "heart" and "lungs" in the List.
the forth sentence is 'the heart size is in noraml limit', which discribes about "heart" in the List.
the fifth sentence is 'bony structures are intact', which discribs about "bones" where were not appeared in the list, so add it in the JSON.
