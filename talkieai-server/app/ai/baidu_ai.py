from typing import List, Dict
import json
import time
from pydantic import BaseModel

from app.ai.interfaces import ChatAI,  MessageBaseAI, MessageInvokeDTO
from app.ai.models import *
from app.core.logging import logging


class BaiduInvokeDTO(BaseModel):
    messages: List[Dict]
    model = "ERNIE-Bot-turbo"


class BaiduAI(MessageBaseAI):
    def __init__(self, client_id: str, client_secret: str, model: str):
        import qianfan

        self.chat_completion = qianfan.ChatCompletion(ak=client_id, sk=client_secret)
        self.model = model

    def _original_invoke_chat(self, dto: MessageInvokeDTO):
        logging.info(f"request_params:{dto.dict()}")
        invoice_dto = BaiduInvokeDTO(messages=dto.messages, model=self.model)
        resp = self.chat_completion.do(**invoice_dto.dict())
        logging.info(f"response:{resp}")
        return {'data': resp["result"]}
