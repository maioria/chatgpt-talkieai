import json
from abc import ABC, abstractmethod

from app.config import Config
from app.core.logging import logging
import os
from typing import Dict, List
import openai
from pydantic import BaseModel, constr

# 设置HTTP和HTTPS代理
# proxy_host = "127.0.0.1"
# proxy_port = "33210"
# os.environ["HTTP_PROXY"] = f"http://{proxy_host}:{proxy_port}"
# os.environ["HTTPS_PROXY"] = f"http://{proxy_host}:{proxy_port}"
os.environ["HTTP_PROXY"] = ''
os.environ["HTTPS_PROXY"] = ''

"""chat_gpt相关调用"""


class ApiKeyModel(BaseModel):
    organization: constr(min_length=10)
    api_key: constr(min_length=10)


class ChatGPTInvokeDTO(BaseModel):
    organization: str = None
    api_key: str = None
    messages: List[Dict]
    model: str = 'gpt-3.5-turbo'
    temperature: float = 0.5
    max_tokens: int = 100


class ChatGptComponent(ABC):
    """调用chatgpt的工具类"""

    @abstractmethod
    def invoke_chat(self, dto: ChatGPTInvokeDTO, key: ApiKeyModel) -> Dict:
        pass


class ChatGptLocalComponent(ChatGptComponent):
    """本地调用chatgpt"""

    def invoke_chat(self, dto: ChatGPTInvokeDTO, key: ApiKeyModel) -> Dict:
        logging.info(f'invoke_chat, param:{json.dumps(dto.dict())}\nkey:{json.dumps(key.dict())}')
        response = openai.ChatCompletion.create(
            api_key=key.api_key,
            organization=key.organization,
            model=dto.model,
            messages=dto.messages
        )
        result = response.choices[0].message.content
        logging.info(f'response:{result}')
        return {'data': result}


class ChatGptRemoteComponent(ChatGptComponent):
    """远程调用chatgpt"""

    def __init__(self):
        import requests
        session = requests.Session()
        session.trust_env = False
        self.session = session

    def invoke_chat(self, dto: ChatGPTInvokeDTO, api_key: ApiKeyModel) -> Dict:
        logging.info(f'request:{dto.dict()}')
        headers = {
            "Content-Type": "application/json",
            "Api-Key": api_key.api_key,
            "Organization": api_key.organization
        }
        url = f'{Config.CHAT_GPT_SERVER}/api/v1/chat'
        remote_result = self.session.post(url, data=json.dumps(dto.dict()), headers=headers)
        result = remote_result.text
        logging.info(f'response:{result}')
        json_result = json.loads(result)
        return json_result
