import json
from abc import ABC, abstractmethod

from app.core.logging import logging
from typing import Dict, List
import openai
from pydantic import BaseModel, constr

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
