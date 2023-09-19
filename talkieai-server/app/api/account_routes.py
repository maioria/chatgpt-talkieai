from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.core import get_current_account
from app.db import get_db
from app.models.account_models import (
    WechatLoginDTO,
    VisitorLoginDTO,
    AccountSettingsDTO,
)
from app.models.response import ApiResponse
from app.services.account_service import AccountService

router = APIRouter()


@router.post("/wechat/code-login", name="Wechat code login")
def wechat_code_login_api(dto: WechatLoginDTO, db: Session = Depends(get_db)):
    """微信小程序登录"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.wechat_login(dto))


@router.post("/visitor-login", name="Visitor login")
def visitor_login(
    request: Request, dto: VisitorLoginDTO, db: Session = Depends(get_db)
):
    """用户访客登录，一个IP只能有一个访客，如果ip已经生成了访客"""
    client_host = request.client.host

    # client_host 不能为空
    if not client_host:
        return ApiResponse(code="400", status="FAILED", message="client_host 不能为空")
    # dto.fingerprint 不能为空
    if not dto.fingerprint:
        return ApiResponse(code="400", status="FAILED", message="dto.fingerprint 不能为空")

    user_agent = request.headers["User-Agent"]
    account_service = AccountService(db)
    return ApiResponse(
        data=account_service.visitor_login(dto.fingerprint, client_host, user_agent)
    )


@router.get("/account-info", name="Get User info")
def get_account_info(
    db: Session = Depends(get_db), account_id: str = Depends(get_current_account)
):
    """获取用户信息"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.get_account_info(account_id))


@router.post("/settings")
def account_settings_api(
    dto: AccountSettingsDTO,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """用户保存设置"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.save_settings(dto, account_id))

@router.get('/settings')
def get_account_settings_api(
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """获取用户设置"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.get_settings(account_id))