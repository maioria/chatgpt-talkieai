from enum import Enum
from typing import List, Dict

from pydantic import BaseModel, constr


class MessageType(Enum):
    """消息类型"""

    ACCOUNT = "ACCOUNT"
    SYSTEM = "SYSTEM"


class WechatLoginDTO(BaseModel):
    code: str = None
    state: str = None


class VisitorLoginDTO(BaseModel):
    fingerprint: constr(min_length=15)


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
    session_id: str = None
    target_language: str = "zh-CN"


class TransformContentSpeechDTO(BaseModel):
    """内容转语音"""

    session_id: str = None
    content: constr(max_length=500)
    speech_role_name: str = "en-US-JennyNeural"
    speech_style: str = "neutral"
    speech_rate: str = "1.0"
    language: str = "en-US"


class GrammarDTO(BaseModel):
    """分析英文的语法错误"""

    message_id: constr(min_length=1)


class PronunciationDTO(BaseModel):
    """语音评估"""

    message_id: constr(min_length=1)


class WordDetailDTO(BaseModel):
    """单词详情"""

    word: constr(min_length=1)


class WordPracticeDTO(BaseModel):
    """单词练习"""

    session_id: str = None
    word: constr(min_length=1)
    file_name: constr(min_length=1)


class CollectDTO(BaseModel):
    """收藏单词或者句子"""

    type: constr(min_length=1)
    message_id: str = None
    content: str = None


class PromptDTO(BaseModel):
    """帮助用户生成提示句"""

    session_id: constr(min_length=1)


class FeedbackDTO(BaseModel):
    content: constr(min_length=1)
    contact: str = None


class AccountSettingsDTO(BaseModel):
    auto_playing_voice: bool = True
    playing_voice_speed: str = "1.0"
    auto_text_shadow: bool = True
    auto_pronunciation: bool = True


class CreateSessionDTO(BaseModel):
    role_name: str
