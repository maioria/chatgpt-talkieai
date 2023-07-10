from enum import Enum

from pydantic import BaseModel, constr


# 用户使用次数类型，包含会话、翻译、语法分析、音标转换、提示句
class AccountUsageType(Enum):
    SESSION = 'SESSION'
    CHAT = 'CHAT'
    SPEECH = 'SPEECH'
    TRANSFORM = 'TRANSFORM'
    TRANSLATE = 'TRANSLATE'
    PROMPT = 'PROMPT'


class AccountStatus(Enum):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'


class Gender(Enum):
    """会话语音的性别"""
    MALE = 'MALE'
    FEMALE = 'FEMALE'


class SessionLanguage(Enum):
    """会话语音的语言"""
    ENGLISH = 'en_US'
    CHINESE = 'cn_ZH'


class SessionSpeechRate(Enum):
    """会话语音的语速"""
    SLOW = 'SLOW'
    NORMAL = 'NORMAL'
    FAST = 'FAST'


class SessionFeel(Enum):
    """会话老师的情绪"""
    NEUTRAL = 'NEUTRAL'
    HAPPY = 'HAPPY'
    SAD = 'SAD'
    ANGRY = 'ANGRY'
    FEARFUL = 'FEARFUL'
    DISGUSTED = 'DISGUSTED'
    SURPRISED = 'SURPRISED'


class MessageType(Enum):
    """消息类型"""
    ACCOUNT = 'ACCOUNT'
    SYSTEM = 'SYSTEM'


class SessionScene(Enum):
    """会话场景，包含普通、旅游、学习、工作、医院其他"""
    NORMAL = 'NORMAL'
    TRAVEL = 'TRAVEL'
    STUDY = 'STUDY'
    WORK = 'WORK'
    OTHER = 'OTHER'


class VisitorLoginDTO(BaseModel):
    fingerprint: constr(min_length=15)


class DemoTranslateDTO(BaseModel):
    """翻译"""
    language: constr(min_length=1)


# 创建会话
class SessionCreateDTO(BaseModel):
    """创建会话"""
    teacher_avatar: str = None
    name: constr(min_length=1)
    scene: SessionScene = SessionScene.NORMAL
    scene_content: str = None
    gender: constr(min_length=1)
    language: constr(min_length=1)
    speech_role_name: constr(min_length=1)
    speech_style: str = None
    speech_rate: str = '1.0'


class ChatDTO(BaseModel):
    """聊天"""
    session_id: str = None
    message: constr(min_length=1)
    file_name: str = None


class SpeechDemoDTO(BaseModel):
    """语音演示"""
    language: constr(min_length=1)
    speech_role_name: constr(min_length=1)
    speech_style: str = None
    speech_rate: str = '1.0'


class TransformSpeechDTO(BaseModel):
    """消息转语音"""
    message_id: constr(min_length=5)


class TranslateDTO(BaseModel):
    """翻译"""
    message_id: constr(min_length=1)


class GrammarDTO(BaseModel):
    """分析英文的语法错误"""
    message_id: constr(min_length=1)


class PromptDTO(BaseModel):
    """帮助用户生成提示句"""
    session_id: constr(min_length=1)
    message_id: constr(min_length=1)
