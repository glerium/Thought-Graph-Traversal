from metrics import compute_scores_single
from collections import defaultdict
import re
import os
import pandas as pd
import json
from typing import Dict, List, Tuple, Union, Any
import numpy as np
import csv
import glob
from tqdm import tqdm
import concurrent.futures
import torch
import sys
import traceback
import time
import chatbot
from datetime import datetime

LOOP = os.environ.get('LOOP', 'error')
assert LOOP != 'error', "Environment variable LOOP must be set."
BOT_TYPE = os.environ.get('BOT_TYPE', 'error')
assert BOT_TYPE != 'error', "Environment variable BOT_TYPE must be set."
assert BOT_TYPE in ['huatuo', 'gpt-4o', 'qwen2.5-vl'], f"Unsupported BOT_TYPE: {BOT_TYPE}. Supported types are: ['huatuo', 'gpt-4o', 'qwen-7b-vision']"

OUT_BASE_DIR = './outputs'
FILE_METRICS_OUT = os.path.join(OUT_BASE_DIR, f'metrics_{LOOP}_{BOT_TYPE}.csv')
FILE_ANSWERS_OUT = os.path.join(OUT_BASE_DIR, f'answers_{LOOP}_{BOT_TYPE}.csv')

DATA_PATH = os.environ.get('DATA_PATH', 'error')
assert DATA_PATH != 'error', "Environment variable DATA_PATH must be set."
GTS_PATH = os.environ.get('GTS_PATH', 'error')
assert GTS_PATH != 'error', "Environment variable GTS_PATH must be set."

os.makedirs(OUT_BASE_DIR, exist_ok=True)

if os.path.exists(FILE_METRICS_OUT):
    try:
        os.remove(FILE_METRICS_OUT)
    except OSError as e:
        print(f"Error removing existing metrics file {FILE_METRICS_OUT}: {e}", file=sys.stderr)

if os.path.exists(FILE_ANSWERS_OUT):
    try:
        os.remove(FILE_ANSWERS_OUT)
    except OSError as e:
        print(f"Error removing existing answers file {FILE_ANSWERS_OUT}: {e}", file=sys.stderr)

    
PROMPT_BASE_DIR = './prompts'

try:
    with open(os.path.join(PROMPT_BASE_DIR, 'prompt_organ.json'), 'r', encoding='utf-8') as f:
        organ_examples = json.load(f)

    with open(os.path.join(PROMPT_BASE_DIR, 'prompt_organ.md'), 'r', encoding='utf-8') as f:
        organ_template = f.read()

    with open(os.path.join(PROMPT_BASE_DIR, 'questions/questions.md'), 'r', encoding='utf-8') as f:
        questions_template = f.read()

    with open(os.path.join(PROMPT_BASE_DIR, 'verify_answer.md'), 'r', encoding='utf-8') as f:
        verify_template = f.read()

    with open(os.path.join(PROMPT_BASE_DIR, 'questions/questions.json'), 'r', encoding='utf-8') as f:
        question_examples = json.load(f)['question']


except FileNotFoundError as e:
    print(f"Error loading prompt files: {e}. Please ensure the directory '{PROMPT_BASE_DIR}' and necessary files exist.", file=sys.stderr)
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"Error decoding JSON in prompt files: {e}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred loading prompt files: {e}", file=sys.stderr)
    sys.exit(1)


organ_examples: Dict[str, Dict[str, List[str]]]
question_examples: List[Dict[str, Union[str, List[str]]]]

def postprocess(answer: str) -> str:
    if not isinstance(answer, str):
        return ""
    answer = answer.replace('.', ' . ').replace(',', ' . ')
    for _ in range(5):
        answer = answer.replace('  ', ' ')
    answer = answer.strip()
    return answer

def process_single_sample_worker(idx: int, sample_id: str, gt: str, image_dir: List[str],
                                 organ_examples: Dict[str, Dict[str, List[str]]], organ_template: str,
                                 question_examples: List[Dict[str, Union[str, List[str]]]], questions_template: str,
                                 device: str) -> Tuple[int, str, int, Union[Dict[str, float], None], str]:
    reasoning_str_all_sample = ''
    answers_all_sample = ''
    final_answer_for_metrics = ""

    try:
        for organ, organ_example_item in organ_examples.items():
            findings_for_organ: List[str] = []
            for q_idx, question_item in enumerate(question_examples, start=1):
                question = question_item['question'].format(organ=organ)
                thought_examples = [str(i).format(organ=organ) if isinstance(i, str) and '{organ}' in i else str(i) for i in question_item.get('thought', [])]
                reply_examples = [str(i).format(organ=organ) if isinstance(i, str) and '{organ}' in i else str(i) for i in question_item.get('reply', [])]

                question_prompt = questions_template.format(
                    organ=organ,
                    question=question,
                    thought_examples=thought_examples,
                    reply_examples=reply_examples
                )
                verified = False
                while not verified:
                    print(1)
                    success, answer, reasoning = chatbot.ask(prompt=question_prompt, 
                                                            image_dirs=image_dir, 
                                                            device=device, 
                                                            bot_type=BOT_TYPE,
                                                            chat_type='ask')
                    answer = answer.replace('.', '').replace(',', '').strip()
                    if not success:
                        return idx, sample_id, 0, None, ""
                    
                    verify_prompt = verify_template.format(
                        question=question,
                        answer=answer,
                        datetime=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    )
                    success, verified = chatbot.ask(prompt=verify_prompt,
                                                    image_dirs=image_dir,
                                                    device=device,
                                                    bot_type=BOT_TYPE,
                                                    chat_type='verify')
                    if not success:
                        return idx, sample_id, 0, None, ""
                
                reasoning_str_all_sample += reasoning
                findings_for_organ.append(answer)

            organ_example_reply = organ_example_item.get('reply', [])
            organ_example_reply_formatted = [str(i).format(organ=organ) if isinstance(i, str) and '{organ}' in i else str(i) for i in organ_example_reply]

            findings_for_organ_str = [str(f) for f in findings_for_organ]

            prompt = organ_template.format(
                organ=organ,
                findings='\n'.join(findings_for_organ_str),
                reply_examples=organ_example_reply_formatted
            )
            success, organ_summary_answer, reasoning = chatbot.ask(prompt=prompt,
                                                                   image_dirs=image_dir, 
                                                                   device=device, 
                                                                   bot_type='huatuo',
                                                                   chat_type='ask')
            if not success:
                return idx, sample_id, 0, None, ""
            reasoning_str_all_sample += reasoning
            answers_all_sample += organ_summary_answer + '.'

        final_answer_for_metrics = postprocess(answers_all_sample)
        final_reasoning_for_metrics = postprocess(reasoning_str_all_sample)
        reasoning_len = final_reasoning_for_metrics.count(' ') + 1 if final_reasoning_for_metrics.strip() else 0

        metric = None
        try:
            gt_str = str(gt)
            metric = compute_scores_single(gt_str, final_answer_for_metrics)

            if not isinstance(metric, dict) or any(not isinstance(v, (int, float)) for v in metric.values()):
                print(f"Worker process {os.getpid()}: compute_scores_single returned invalid format for sample {sample_id} ({idx}): {metric}", file=sys.stderr)
                metric = None

        except Exception as e:
            print(f"Worker process {os.getpid()}: Error computing metrics for sample {sample_id} ({idx}): {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            metric = None

        return idx, sample_id, reasoning_len, metric, final_answer_for_metrics

    except Exception as e:
        print(f"Worker process {os.getpid()}: Unhandled error during sample processing for sample {sample_id} ({idx}): {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return idx, sample_id, 0, None, ""


if __name__ == '__main__':
    try:
        NUM_GPUS = torch.cuda.device_count()
        if NUM_GPUS == 0:
            print("Error: No CUDA devices available. Exiting.", file=sys.stderr)
            sys.exit(1)
        print(f"Found {NUM_GPUS} CUDA devices.")
    except Exception as e:
        print(f"Error checking CUDA devices: {e}", file=sys.stderr)
        print("Please ensure torch is installed and configured correctly for CUDA.", file=sys.stderr)
        sys.exit(1)

    try:
        data_gts = pd.read_table(GTS_PATH, sep='\t', names=['sample_id', 'text'], header=None, encoding='utf-8')
        if data_gts.empty:
            print(f"Warning: {GTS_PATH} is empty.", file=sys.stderr)
    except FileNotFoundError:
        print(f"Error: {GTS_PATH} not found. Please ensure the file exists.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error loading {GTS_PATH}: {e}", file=sys.stderr)
        sys.exit(1)


    try:
        with open(FILE_METRICS_OUT, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'sample_id', 'reasoning_len', 'BLEU_1', 'BLEU_2', 'BLEU_3', 'BLEU_4', 'METEOR', 'ROUGE_L'])
    except IOError as e:
        print(f"Error writing header to metrics output file {FILE_METRICS_OUT}: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(FILE_ANSWERS_OUT, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['sample_id', 'answer'])
    except IOError as e:
        print(f"Error writing header to answers output file {FILE_ANSWERS_OUT}: {e}", file=sys.stderr)
        sys.exit(1)


    with concurrent.futures.ProcessPoolExecutor(max_workers=NUM_GPUS) as executor:
        futures = {}
        print(f"Submitting {len(data_gts)} samples to ProcessPoolExecutor...")

        for idx, row in enumerate(data_gts.itertuples(index=False, name='Sample')):
            sample_id = row.sample_id
            gt = row.text
            image_dir = glob.glob(os.path.join(DATA_PATH, f'{sample_id}/*.jpg'))
            device = f'cuda:{idx % NUM_GPUS}'

            future = executor.submit(process_single_sample_worker, idx, sample_id, gt, image_dir,
                                      organ_examples, organ_template, question_examples, questions_template,
                                      device)
            futures[future] = (idx, sample_id)


        print("Collecting and writing results immediately as they complete (skipping metrics on errors)...")
        try:
            with open(FILE_METRICS_OUT, 'a', newline='', encoding='utf-8', buffering=1) as f_metrics_out, \
                 open(FILE_ANSWERS_OUT, 'a', newline='', encoding='utf-8', buffering=1) as f_answers_out:

                metrics_writer = csv.writer(f_metrics_out)
                answers_writer = csv.writer(f_answers_out)

                for future in tqdm(concurrent.futures.as_completed(futures), total=len(data_gts), desc="Processing samples"):
                    idx, sample_id = futures[future]
                    try:
                        result_idx, result_sample_id, reasoning_len, metric, final_answer = future.result()

                        try:
                            answers_writer.writerow([result_sample_id, final_answer])
                        except IOError as e:
                            print(f"Error writing answer for sample {result_sample_id} ({result_idx}) to {FILE_ANSWERS_OUT}: {e}", file=sys.stderr)

                        if metric is not None:
                            try:
                                row_data = [result_idx, result_sample_id, reasoning_len]
                                row_data.extend([metric.get('BLEU_1', 0.0), metric.get('BLEU_2', 0.0),
                                                 metric.get('BLEU_3', 0.0), metric.get('BLEU_4', 0.0),
                                                 metric.get('METEOR', 0.0), metric.get('ROUGE_L', 0.0)])

                                metrics_writer.writerow(row_data)
                            except IOError as e:
                                print(f"Error writing metrics for sample {result_sample_id} ({result_idx}) to {FILE_METRICS_OUT}: {e}", file=sys.stderr)

                        else:
                            print(f'Skipping writing metrics for sample {result_sample_id} ({result_idx}) due to processing or metric calculation error in worker.', file=sys.stderr)

                    except Exception as exc:
                        print(f'Sample {sample_id} ({idx}) processing failed severely in worker: {exc}', file=sys.stderr)
                        traceback.print_exc(file=sys.stderr)
                exit()

        except IOError as e:
            print(f"Error opening output files: {e}", file=sys.stderr)
        except Exception as e:
            print(f"An unexpected error occurred while collecting or writing results: {e}", file=sys.stderr)

    print("Processing complete.")
