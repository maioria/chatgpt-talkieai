from typing import List, Dict
import json
from pydantic import BaseModel

from app.ai.interfaces import SystemBaseAI, MessageInvokeDTO
from app.ai.models import *
from app.core.logging import logging

class ChatGPTInvokeDTO(BaseModel):
    messages: List[Dict]
    model: str = 'gpt-3.5-turbo'
    temperature: float = 0.5
    max_tokens: int = 100

class ChatGptRemoteAI(SystemBaseAI):
    """ 通过http远程调用的接口 """
    def __init__(self, api_key:str, organization:str,server_url :str):
        import requests

        session = requests.Session()
        session.trust_env = False
        self.session = session
        self.api_key = api_key
        self.organization = organization
        self.server_url = server_url

    def _original_invoke_chat(self, dto: MessageInvokeDTO):
        headers = {
            "Content-Type": "application/json",
            "Api-Key": self.api_key,
            "Organization": self.organization
        }
        url = f'{self.server_url}/api/v1/chat'
        request_dto = ChatGPTInvokeDTO(messages=dto.messages)
        logging.info(f'request_dto:{request_dto.dict()}')
        remote_result = self.session.post(url, data=json.dumps(request_dto.dict()), headers=headers)
        result = remote_result.text
        logging.info(f'response:{result}')
        json_result = json.loads(result)
        return json_result

class ChatGptLocalAI(SystemBaseAI):
    """本地直接调用openai的接口"""
    def __init__(self, api_key:str, organization:str):
        import openai

        self.api_key = api_key
        self.organization = organization
        self.openai = openai

    def _original_invoke_chat(self, dto: MessageInvokeDTO):
        request_dto = ChatGPTInvokeDTO(messages=dto.messages)
        logging.info(f'request_dto:{request_dto.dict()}')
        response = self.openai.ChatCompletion.create(
            api_key=self.api_key,
            organization=self.organization,
            model=request_dto.model,
            messages=request_dto.messages
        )
        result = response.choices[0].message.content
        return {'data': result}
