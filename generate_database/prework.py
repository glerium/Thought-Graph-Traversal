from collections import defaultdict
from typing import Dict, List
from openai_utils import OpenAIUtils
import pandas as pd
import json
import os

organs = ['cardiomediastinal silhouette', 'heart', 'lungs', 'pneumothorax', 'pleural effusion']
with open('data.json','r') as f:
    tot_data = json.load(f)['train']
with open('prompt.md','r') as f:
    slc_organ = f.read()

FILE_DATABASE = 'expert_database.json'
FILE_OUT = 'out.txt'

if os.path.exists(FILE_DATABASE):
    os.remove(FILE_DATABASE)
if os.path.exists(FILE_OUT):
    os.remove(FILE_OUT)

expert_database = {}
expert_database['organ_list'] = organs
expert_database['database'] = defaultdict(dict)
for organ in organs:
    expert_database['database'][organ] = {
        "size": 0,
        "database": []
    }

with open(FILE_DATABASE, 'w') as f:
    json.dump(expert_database, f, indent=4)


for idx, item in enumerate(tot_data):
    if idx != 0 and tot_data[idx]['study_id'] == tot_data[idx-1]['study_id']:
        continue
    # format
    report = item['report']
    report = report.replace('impression: ', '').replace('Findings: ', '').replace('\n', '')
    for i in range(1, 10):
        report = report.replace(str(i), '')
    format_organ_list = json.dumps({organ: [] for organ in organs})
    prompt = slc_organ.format(report=report,
                              organ_list=str(organs),
                              format_organ_list=format_organ_list)
    
    system_prompt = 'You are an assistant responsible for performing simple tasks. Now, please locate the positions of each organ from the **List** in the **Report** and return the results in JSON format.'
    while True:
        try:
            answer = OpenAIUtils.ask(msg=prompt,
                                     system_prompt=system_prompt,
                                     temperature=0.2,
                                     client=OpenAIUtils.client)[0]
            answer = answer.replace('```json', '').replace('```', '')
            with open(FILE_OUT, 'a+') as f:
                f.write(str(idx)+" ..."+"\n")
                f.write(str(report)+"\n")
                f.write(answer+"\n")
            
            answer = json.loads(answer)
            assert 'list' in answer.keys()

            break

        except Exception as e:
            print(f'Error!')
            print(e)
            
    for key in answer['list']:
        key = key.lower()
        if key not in organs:
            organs.append(key)
            expert_database['database'][key]['size'] = 0
            expert_database['database'][key]['database'] = []
            expert_database['organ_list'] = organs
    
    # print(expert_database['database'])
    for org in organs:
        if org not in answer['list']:
            continue
        for i in answer['list'][org]:
            key = list(answer['sentence'].keys())[i - 1]
            sentences = answer['sentence'][key]
            # print(expert_database['database'][key], )
            expert_database['database'][org]['database'].append(sentences[0])
        expert_database['database'][org]['size'] = len(expert_database['database'][org]['database'])
                
    with open(FILE_DATABASE, 'w') as f:
        json.dump(expert_database, f, indent=4)
