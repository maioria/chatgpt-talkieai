from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core import get_current_account
from app.db import get_db
from app.models.account_models import (
    FeedbackDTO,
)
from app.models.response import ApiResponse
from app.services.account_service import AccountService

router = APIRouter()

@router.post("/feedback")
def add_feedback(
    dto: FeedbackDTO,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """用户反馈"""
    account_service = AccountService(db)
    account_service.add_feedback(dto, account_id)
    return ApiResponse(data="SUCCESS")
