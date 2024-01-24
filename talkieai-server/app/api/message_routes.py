from fastapi import APIRouter, Depends, Response

from sqlalchemy.orm import Session
from app.core import get_current_account
from app.core.utils import *
from app.db import get_db
from app.models.account_models import *
from app.models.chat_models import *
from app.models.response import ApiResponse
from app.services.account_service import AccountService
from app.services.chat_service import ChatService

router = APIRouter()


@router.post("/messages/{message_id}/practice")
def message_practice_api(
    message_id: str,
    dto: MessagePracticeDTO,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """发送消息"""
    chat_service = ChatService(db)
    return ApiResponse(
        data=chat_service.message_practice(message_id, dto, account_id)
    )


@router.post("/messages/{message_id}/translate")
def translate_api(
    message_id: str,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """翻译成用户的源语言"""
    chat_service = ChatService(db)
    return ApiResponse(data=chat_service.translate_message(message_id, account_id))


@router.get("/message/speech")
def speech_api(
    message_id: str,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """消息转语音"""
    chat_service = ChatService(db)
    speech_result = chat_service.message_speech(message_id, account_id)
    """获取文件"""
    file_path = voice_file_get_path(speech_result["file"])
    # 判断文件是否存在
    with open(file_path, "rb") as file:
        contents = file.read()
        headers = {
            "Content-Type": "audio/wav",
            "Content-Disposition": "attachment",
            "filename": speech_result["file"],
        }
        return Response(
            content=contents, media_type="application/octet-stream", headers=headers
        )


@router.post("/message/translate-source-language")
def translate_source_language(
    dto: TranslateTextDTO,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """翻译成用户本身的语言"""
    chat_service = ChatService(db)
    return ApiResponse(data=chat_service.translate_source_language(dto, account_id))


@router.post("/message/translate-setting-language")
def translate_setting_language(
    dto: TranslateTextDTO,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """翻译成用户学习的语言"""
    chat_service = ChatService(db)
    return ApiResponse(data=chat_service.translate_setting_language(dto, account_id))


@router.get("/message/speech-content")
def speech_content_api(
    content: str,
    session_id: str = None,
    speech_role_name: str = None,
    speech_role_style: str = None,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """消息转语音"""
    chat_service = ChatService(db)
    speech_result = chat_service.message_speech_content(
        TransformContentSpeechDTO(
            content=content, speech_role_name=speech_role_name, speech_role_style=speech_role_style, session_id=session_id
        ),
        account_id,
    )
    """获取文件"""
    file_path = voice_file_get_path(speech_result["file"])
    # 判断文件是否存在
    with open(file_path, "rb") as file:
        contents = file.read()
        headers = {
            "Content-Type": "audio/wav",
            "Content-Disposition": "attachment",
            "filename": speech_result["file"],
        }
        return Response(
            content=contents, media_type="application/octet-stream", headers=headers
        )


@router.post("/message/grammar")
def grammar_api(
    dto: GrammarDTO,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """分析语法错误"""
    chat_service = ChatService(db)
    return ApiResponse(data=chat_service.grammar_analysis(dto, account_id))


# 进行发音评估
@router.post("/message/pronunciation")
def pronunciation_api(
    dto: PronunciationDTO,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """进行发单评估"""
    chat_service = ChatService(db)
    return ApiResponse(data=chat_service.pronunciation(dto, account_id))


# 进行音素级别的发音评估


# 获取单词的音标与翻译
@router.post("/message/word/detail")
def get_word_api(
    dto: WordDetailDTO,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """获取单词的音标与翻译"""
    chat_service = ChatService(db)
    return ApiResponse(data=chat_service.get_word(dto, account_id))


# 单词练习
@router.post("/message/word/practice")
def word_practice_api(
    dto: WordPracticeDTO,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """单词练习"""
    chat_service = ChatService(db)
    return ApiResponse(data=chat_service.word_practice(dto, account_id))


# 帮助用户生成提示句
@router.post("/message/prompt")
def prompt_api(
    dto: PromptDTO,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """帮助用户生成提示句"""
    chat_service = ChatService(db)
    return ApiResponse(data=chat_service.prompt_sentence(dto, account_id))
