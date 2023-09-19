import json
from abc import ABC, abstractmethod

from app.config import Config
from app.core.logging import logging
import os
from typing import Dict, List, Generator
import openai
from pydantic import BaseModel, constr


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
    @abstractmethod
    def invoke_chat(self, dto: ChatGPTInvokeDTO, key: ApiKeyModel) -> Dict:
        pass

    @abstractmethod
    async def invoke_chat_stream(self, dto: ChatGPTInvokeDTO, key: ApiKeyModel):
        pass


class ChatGptLocalComponent(ChatGptComponent):
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

    def invoke_chat_stream(self, dto: ChatGPTInvokeDTO, key: ApiKeyModel):
        logging.info(f'invoke_chat, param:{json.dumps(dto.dict())}\nkey:{json.dumps(key.dict())}')
        response = openai.ChatCompletion.create(
            api_key=key.api_key,
            organization=key.organization,
            model=dto.model,
            messages=dto.messages,
            n=1,
            stream=True
        )
        for chunk in response:
            if chunk.choices and chunk.choices[0] and chunk.choices[0]['delta']:
                delta = chunk.choices[0]['delta']
                item_data = {
                    "id": chunk['id'],
                    "data": delta.content,
                    "ended": 'false'
                }
            else:
                item_data = {
                    "id": chunk['id'],
                    "ended": 'true'
                }
            yield item_data
