from openai import OpenAI
from typing import List
import base64
import os

class OpenAIUtils:
    gpt_client = OpenAI(
        api_key=os.environ.get('OPENAI_API_KEY', None)
    )
    qwen_client = OpenAI(
        api_key=os.environ.get('ALIYUN_API_KEY', None),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    @classmethod
    def ask(cls,
            msg: str,
            system_prompt: str = 'You are a helpful assistant.',
            image_dir: List[str] = None,
            max_token: int = None,
            model: str = "gpt-4o",
            n: int = 1,
            temperature: float = None,
            client: OpenAI = gpt_client) -> List[str]:
        user_content = []

        user_content.append({
            "type": "text",
            "text": msg
        })

        if image_dir is not None and isinstance(image_dir, list) and len(image_dir) > 0:
            for image in image_dir:
                with open(image, "rb") as img_file:
                    base64_image = base64.b64encode(img_file.read()).decode("utf-8")

                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}"
                    }
                })
        else:
            print('No image appended.')

        kwargs = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "model": model,
            "n": n,
        }

        if max_token is not None:
            kwargs["max_tokens"] = max_token
        if temperature is not None:
            kwargs["temperature"] = temperature

        print('asking')
        chat_completion = client.chat.completions.create(**kwargs)
        print('asked')

        ret = [chat_completion.choices[i].message.content for i in range(n)]
        return ret

    @classmethod
    def get_embedding(cls, sentence: str):
        response = cls.client.embeddings.create(
            input=sentence,
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding
