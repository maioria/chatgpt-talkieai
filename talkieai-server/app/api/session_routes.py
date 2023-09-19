import os

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core import get_current_account
from app.db import get_db
from app.models.response import ApiResponse
from app.services.account_service import AccountService
from app.models.account_models import (
    CreateSessionDTO
)

router = APIRouter()

@router.post("/sessions")
def create_session(
    dto: CreateSessionDTO,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """创建会话"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.create_session(dto, account_id))


@router.get("/sessions/default")
def get_default_session(
    db: Session = Depends(get_db), account_id: str = Depends(get_current_account)
):
    """获取默认会话"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.get_default_session(account_id))


# 

@router.get("/sessions/{session_id}")
def get_session(
    session_id: str,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """获取会话详情"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.get_session(session_id, account_id))