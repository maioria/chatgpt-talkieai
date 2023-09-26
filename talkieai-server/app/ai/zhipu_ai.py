from typing import List, Dict
import json
import time
from pydantic import BaseModel

from app.ai.interfaces import ChatAI,  MessageBaseAI, MessageInvokeDTO
from app.ai.models import *
from app.core.logging import logging


class ZhipuInvokeDTO(BaseModel):
    prompt: List[Dict]
    model = "chatglm_pro"


class ZhipuAI(MessageBaseAI):
    def __init__(self, api_key: str, model:str):
        import zhipuai

        zhipuai.api_key = api_key
        self.zhipuai = zhipuai
        self.model = model

    def _original_invoke_chat(self, dto: MessageInvokeDTO):
        logging.info(f"request_params:{dto.dict()}")
        invoke_dto = ZhipuInvokeDTO(prompt=dto.messages, model=self.model)
        resp = self.zhipuai.model_api.invoke(**invoke_dto.dict())
        logging.info(f"response:{resp}")

        if (resp["code"] != 200):
            raise Exception(resp["msg"])

        result = resp["data"]["choices"][0]["content"]
        # 去掉俩边的 “”
        result = result.strip('"')
        # 去掉json的转义字符
        result = result.replace('\\"', '"').replace('\\n', '\n').replace('\\', '')
        print(f'format:{result}')
        return {'data': result}
