from fastapi import APIRouter, Depends, Response

from sqlalchemy.orm import Session
from app.core import get_current_account
from app.core.utils import *
from app.db import get_db
from app.models.account_models import *
from app.models.response import ApiResponse
from app.services.account_service import AccountService
from app.services.chat_service import ChatService

router = APIRouter()


@router.get("/sessions/default")
def get_default_session(
    db: Session = Depends(get_db), account_id: str = Depends(get_current_account)
):
    """获取默认会话"""
    chat_service = ChatService(db)
    return ApiResponse(data=chat_service.get_default_session(account_id))


@router.get("/sessions/{session_id}")
def get_session(
    session_id: str,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """获取会话详情"""
    chat_service = ChatService(db)
    return ApiResponse(data=chat_service.get_session(session_id, account_id))


@router.post("/sessions/{session_id}/voice-translate")
def voice_upload_api(
    session_id: str,
    dto: VoiceTranslateDTO,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """语音解析成文字"""
    chat_service = ChatService(db)
    return ApiResponse(data=chat_service.transform_text(session_id, dto, account_id))


# 获取ai的第一句问候语
@router.get("/sessions/{session_id}/greeting")
def get_session_greeting(
    session_id: str,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """获取会话消息"""
    chat_service = ChatService(db)
    return ApiResponse(data=chat_service.get_session_greeting(session_id, account_id))


@router.post("/sessions/{session_id}/chat")
def chat_api(
    session_id: str,
    dto: ChatDTO,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """发送消息"""
    chat_service = ChatService(db)
    return ApiResponse(
        data=chat_service.send_session_message(session_id, dto, account_id)
    )

# 删除最近俩次的对话
@router.delete("/sessions/{session_id}/messages/latest")
def delete_latest_session_messages(
    session_id: str,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """删除最近一次的对话"""
    chat_service = ChatService(db)
    return ApiResponse(
        data=chat_service.delete_latest_session_messages(session_id, account_id)
    )

# 删除session下所有的对话
@router.delete("/sessions/{session_id}/messages")
def delete_all_session_messages(
    session_id: str,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """删除最近一次的对话"""
    chat_service = ChatService(db)
    return ApiResponse(
        data=chat_service.delete_all_session_messages(session_id, account_id)
    )