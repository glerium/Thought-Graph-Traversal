from openai import OpenAI
import httpx

from typing import List
import base64
import json

with open('config.json', 'r') as f:
    config = json.load(f)

class OpenAIUtils:
    proxy_url = "http://127.0.0.1:7890"
    if config['proxy']['use_proxy']:
        client = OpenAI(
            api_key=config['api']['openai-apikey'],
            http_client=httpx.Client(proxy=proxy_url)
        )
    else:
        client = OpenAI(
            api_key=config['api']['openai-apikey'],
        )

    @classmethod
    def ask(cls,
            msg: str,
            system_prompt: str,
            image_dir: List[str] = None,
            max_token: int = None,
            model: str = "gpt-4o",
            n: int = 1,
            temperature: float = 0.2,
            client: OpenAI = client) -> List[str]:
        user_content = []

        # 文本内容
        user_content.append({
            "type": "text",
            "text": msg
        })

        # 如果有图片，添加图片内容
        if image_dir is not None and isinstance(image_dir, list) and len(image_dir) > 0:
            for image in image_dir:
                # print(f'Appended {image}')
                with open(image, "rb") as img_file:
                    base64_image = base64.b64encode(img_file.read()).decode("utf-8")

                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}"
                    }
                })
        # else:
        #     print('No image appended.')

        kwargs = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "model": model,
            "n": n,
            "temperature": temperature,
        }

        if max_token is not None:
            kwargs["max_tokens"] = max_token

        print('asking')
        chat_completion = client.chat.completions.create(**kwargs)
        print('asked')
        # print(chat_completion)

        # print(chat_completion)
        ret = [chat_completion.choices[i].message.content for i in range(n)]
        return ret

    @classmethod
    def get_embedding(cls, sentence: str):
        response = cls.client.embeddings.create(
            input=sentence,
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding
