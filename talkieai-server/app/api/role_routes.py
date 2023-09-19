import os

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core import get_current_account
from app.db import get_db
from app.models.response import ApiResponse
from app.services.account_service import AccountService

router = APIRouter()


@router.get("/languages")
def get_settings_languages(
    db: Session = Depends(get_db), account_id: str = Depends(get_current_account)
):
    """获取支持的语言"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.get_settings_languages(account_id))

@router.get("/languages/example")
def get_settings_languages_example(
    language: str,
    db: Session = Depends(get_db), account_id: str = Depends(get_current_account)
):
    """获取支持的语言"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.get_settings_languages_example(language, account_id))

# 获取语言下支持的角色
@router.get("/roles")
def get_settings_roles(
    locale: str,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """获取支持的角色"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.get_settings_roles(locale, account_id))
