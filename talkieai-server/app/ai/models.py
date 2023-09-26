from enum import Enum
from pydantic import BaseModel
from typing import List, Dict

class ChatType(Enum):
    """聊天类型"""
    CHAT = "CHAT"
    TRANSLATE = "TRANSLATE"
    GRAMMAR_ANALYSIS = "GRAMMAR_ANALYSIS"
    WORD_DETAIL = "WORD_DETAIL"
    GREETING = "GREETING"

class ChatParams(BaseModel) :
    prompt_type: ChatType
    prompt_type_params: Dict = {}
    messages: List[Dict] = []

class MessageParams(BaseModel):
    language: str
    name: str
    messages: List[Dict] = [] 

class TranslateParams(BaseModel):
    target_language: str
    content: str

class GreetParams(BaseModel):
    language: str

class GrammarAnalysisParams(BaseModel):
    language: str
    content: str

class PromptSentenceParams(BaseModel):
    language: str
    messages: List[Dict] = []

class WordDetailParams(BaseModel):
    word: str    