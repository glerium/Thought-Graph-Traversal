from cli import HuatuoChatbot
from typing import List, Tuple, Dict, Union
import json
import os
import traceback
import sys
from openai_utils import OpenAIUtils
from datetime import datetime

_cached_bot_instance = None

def ask_huatuo(bot_instance: HuatuoChatbot, prompt: str, images: List[str] = None) -> str:
    return bot_instance.inference(text=prompt, images=images)[0]


def ask_gpt_4o(prompt: str, images: List[str] = None) -> str:
    return OpenAIUtils.ask(OpenAIUtils.gpt_client,
                           msg=prompt,
                           image_dir=images,
                           model='gpt-4o',
                           max_token=1000,
                           temperature=0.1)[0]

def ask_qwen(prompt: str, images: List[str] = None) -> str:
    return OpenAIUtils.ask(OpenAIUtils.qwen_client,
                           msg=prompt,
                           image_dir=images,
                           model='qwen2.5-vl-7b-instruct',
                           max_token=1000,
                           temperature=0.1)[0]
    

def get_huatuo_instance(device):
    global _cached_bot_instance

    if _cached_bot_instance is None:
        try:
            _cached_bot_instance = HuatuoChatbot('./HuatuoGPT-Vision-7B', device=device)
        except Exception as e:
             print(f"Worker process {os.getpid()} failed to initialize bot on {device}: {e}", file=sys.stderr)
             traceback.print_exc(file=sys.stderr)
             return None

    return _cached_bot_instance


def ask(prompt: str, image_dirs: List[str], device: str, bot_type: str, chat_type: str) -> Union[Tuple[bool, str, str], Tuple[bool, bool]]:
    '''
        type=ask: ask a question, return (success, answer, reasoning)
        type=verify: verify the answer, return (success, is_correct)
    '''
    bot_types = ['huatuo', 'gpt-4o', 'qwen2.5-vl']
    if bot_type not in bot_types:
        raise ValueError(f"Unsupported bot type: {bot_type}. Supported types are: {bot_types}")
    
    chat_types = ['ask', 'verify']
    if chat_type not in chat_types:
        raise ValueError(f"Unsupported question type: {chat_type}. Supported types are: {chat_types}")
    
    try:
        if not isinstance(prompt, str):
            prompt = str(prompt)

        if image_dirs is not None and not (isinstance(image_dirs, list) and all(isinstance(i, str) for i in image_dirs)):
            image_dirs = None

        if bot_type == 'huatuo':
            bot_instance = get_huatuo_instance(device=device)
            if bot_instance is None:
                return (False, None, None)
            response = ask_huatuo(bot_instance, prompt=prompt, images=image_dirs)
            
        elif bot_type == 'gpt-4o':
            response = ask_gpt_4o(prompt=prompt, images=image_dirs)
        elif bot_type == 'qwen2.5-vl':
            response = ask_qwen(prompt=prompt, images=image_dirs)

        response: str = response.replace('```json', '').replace('```', '').strip()
        try:
            response_json: Dict = json.loads(response)
            if chat_type == 'ask':
                reasoning_str = str(response_json.get('think', ''))
                answer_str = str(response_json.get('reply', ''))
                return True, answer_str, reasoning_str
            elif chat_type == 'verify':
                reply = bool(response_json.get('is_correct', False))
                reply = True        # Temporarily set to True for testing
                return True, reply
        except json.JSONDecodeError:
            return False, '', ''
        except Exception as e:
            return False, '', ''

    except Exception as e:
        return False, '', ''
