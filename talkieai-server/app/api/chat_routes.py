import os
from fastapi import APIRouter, Depends, Response
from fastapi.responses import StreamingResponse

from sqlalchemy.orm import Session
from app.core import get_current_account
from app.db import get_db
from app.config import Config
from app.core.logging import logging
from app.models.account_models import (
    ChatDTO,
    TransformSpeechDTO,
    VoiceTranslateDTO,
    TranslateDTO,
    TransformContentSpeechDTO,
    GrammarDTO,
    PronunciationDTO,
    WordDetailDTO,
    WordPracticeDTO,
    PromptDTO,
    TranslateTextDTO,
    MessagePracticeDTO
)
from app.models.response import ApiResponse
from app.services.account_service import AccountService

router = APIRouter()


@router.get("/sessions/{session_id}/messages")
def get_session_messages(
    session_id: str,
    page: int = 1,
    page_size: int = 100,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """获取会话消息"""
    account_service = AccountService(db)
    return ApiResponse(
        data=account_service.get_session_messages(
            session_id, account_id, page, page_size
        )
    )

@router.post("/sessions/{session_id}/voice-translate")
def voice_upload_api(
    session_id: str,
    dto: VoiceTranslateDTO,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """语音解析成文字"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.transform_text(session_id, dto, account_id))

# 获取ai的第一句问候语
@router.get("/sessions/{session_id}/greeting")
def get_session_greeting(
    session_id: str,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """获取会话消息"""
    account_service = AccountService(db)
    return ApiResponse(
        data=account_service.get_session_greeting(session_id, account_id)
    )

@router.post("/{session_id}/chat")
def chat_api(
    session_id: str,
    dto: ChatDTO,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """发送消息"""
    account_service = AccountService(db)
    return ApiResponse(
        data=account_service.send_session_message(session_id, dto, account_id)
    )

@router.post("/message/{message_id}/practice")
def message_practice_api(
    message_id: str,
    dto: MessagePracticeDTO,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """发送消息"""
    account_service = AccountService(db)
    return ApiResponse(
        data=account_service.message_practice(message_id, dto, account_id)
    )    

@router.get("/speech")
def speech_api(
    message_id: str,
    db: Session = Depends(get_db), 
    response: Response = Response(),
    account_id: str = Depends(get_current_account)):
    """消息转语音"""
    logging.info("接收数据")
    account_service = AccountService(db)
    speech_result = account_service.message_speech(message_id, account_id)
    """获取文件"""
    file_path = f"{Config.TEMP_SAVE_FILE_PATH}/{speech_result['file']}"
    # 判断文件是否存在
    with open(file_path, "rb") as file:
        contents = file.read()
        headers = {
            "Content-Type": "audio/wav",
            "Content-Disposition": "attachment",
            "filename": speech_result['file']
        }
        logging.info("开始返回")
        return Response(content=contents, media_type="application/octet-stream", headers=headers)


@router.post("/translate")
def translate_api(
    dto: TranslateDTO,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """翻译"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.translate(dto, account_id))


@router.post("/translate-text")
def translate_text_api(
    dto: TranslateTextDTO,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """翻译"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.translate_text(dto, account_id))


@router.get("/speech-content")
def speech_content_api(
    content: str,
    session_id: str = None,
    speech_role_name:str = "en-US-JennyNeural",
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """消息转语音"""
    account_service = AccountService(db)
    speech_result = data=account_service.message_speech_content(TransformContentSpeechDTO(content=content, speech_role_name=speech_role_name, session_id=session_id), account_id)
    """获取文件"""
    file_path = f"{Config.TEMP_SAVE_FILE_PATH}/{speech_result['file']}"
    logging.info(file_path)
    # 判断文件是否存在
    with open(file_path, "rb") as file:
        contents = file.read()
        headers = {
            "Content-Type": "audio/wav",
            "Content-Disposition": "attachment",
            "filename": speech_result['file']
        }
        logging.info("开始返回")
        return Response(content=contents, media_type="application/octet-stream", headers=headers)




@router.post("/grammar")
def grammar_api(
    dto: GrammarDTO,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """分析语法错误"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.grammar_analysis(dto, account_id))


# 进行发音评估
@router.post("/pronunciation")
def pronunciation_api(
    dto: PronunciationDTO,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """进行发单评估"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.pronunciation(dto, account_id))


# 获取单词的音标与翻译
@router.post("/word/detail")
def get_word_api(
    dto: WordDetailDTO,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """获取单词的音标与翻译"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.get_word(dto, account_id))

# 单词练习
@router.post("/word/practice")
def word_practice_api(
    dto: WordPracticeDTO,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """单词练习"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.word_practice(dto, account_id))    


# 删除最近俩次的对话
@router.delete("/sessions/{session_id}/messages/latest")
def delete_latest_session_messages(
    session_id: str,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """删除最近一次的对话"""
    account_service = AccountService(db)
    return ApiResponse(
        data=account_service.delete_latest_session_messages(session_id, account_id)
    )


# 删除session下所有的对话
@router.delete("/sessions/{session_id}/messages")
def delete_all_session_messages(
    session_id: str,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """删除最近一次的对话"""
    account_service = AccountService(db)
    return ApiResponse(
        data=account_service.delete_all_session_messages(session_id, account_id)
    )


# 帮助用户生成提示句
@router.post("/prompt")
def prompt_api(
    dto: PromptDTO,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """帮助用户生成提示句"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.prompt_sentence(dto, account_id))



