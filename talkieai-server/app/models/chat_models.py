from enum import Enum
from typing import List, Dict

from pydantic import BaseModel, constr


class MessageType(Enum):
    """消息类型"""

    ACCOUNT = "ACCOUNT"
    SYSTEM = "SYSTEM"
    # 智谱AI的第一句提示词
    PROMPT = "PROMPT"


class CreateTalkSessionDTO(BaseModel):
    language: str
    short_name: str
    style: str = ""


class CreateSessionDTO(BaseModel):
    topic_id: str


class ChatDTO(BaseModel):
    """聊天"""

    message: str = None
    file_name: str = None


class MessagePracticeDTO(BaseModel):
    """句子练习"""

    file_name: str = None


class TransformSpeechDTO(BaseModel):
    """消息转语音"""

    message_id: constr(min_length=5)


class VoiceTranslateDTO(BaseModel):
    """语音转文字"""

    file_name: constr(min_length=1)


class TranslateDTO(BaseModel):
    """翻译"""

    message_id: constr(min_length=1)


class TranslateTextDTO(BaseModel):
    """翻译"""

    text: constr(min_length=1)


class TransformContentSpeechDTO(BaseModel):
    """内容转语音"""

    session_id: str | None = None
    content: constr(max_length=500)
    speech_role_name: str | None = None
    speech_role_style: str | None = None
    speech_style: str = ""
    speech_rate: str = "1.0"


class GrammarDTO(BaseModel):
    """分析英文的语法错误"""

    message_id: constr(min_length=1)


class PronunciationDTO(BaseModel):
    """语音评估"""
    message_id: constr(min_length=1)


class WordDetailDTO(BaseModel):
    """单词详情"""

    language: str = "en-US"
    session_id: str = None
    word: constr(min_length=1)


class WordPracticeDTO(BaseModel):
    """单词练习"""

    session_id: str = None
    word: constr(min_length=1)
    file_name: constr(min_length=1)


class PromptDTO(BaseModel):
    """帮助用户生成提示句"""

    session_id: constr(min_length=1)
