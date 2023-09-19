from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core import get_current_account
from app.db import get_db
from app.models.account_models import (
    CollectDTO,
)
from app.models.response import ApiResponse
from app.services.account_service import AccountService

router = APIRouter()


@router.get("/collect")
def get_account_collect_api(
    type: str,
    message_id: str = None,
    content: str = None,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """获取用户收藏状态"""
    account_service = AccountService(db)
    return ApiResponse(
        data=account_service.get_collect(
            CollectDTO(type=type, message_id=message_id, content=content), account_id
        )
    )


@router.post("/collect")
def account_collect_api(
    dto: CollectDTO,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """用户保存单词与句子的接口"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.collect(dto, account_id))


@router.delete("/collect")
def account_collect_api(
    dto: CollectDTO,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """取消用户保存的单词或者句子"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.cancel_collect(dto, account_id))


@router.get("/collects")
def get_account_collects_api(
    type: str,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """获取用户收藏的列表信息，包含分页效果"""
    account_service = AccountService(db)
    return ApiResponse(
        data=account_service.get_collects(type, page, page_size, account_id)
    )
