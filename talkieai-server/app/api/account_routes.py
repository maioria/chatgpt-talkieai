from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.core import get_current_account
from app.db import get_db
from app.models.account_models import *
from app.models.response import ApiResponse
from app.services.account_service import AccountService
from app.services.chat_service import ChatService

router = APIRouter()


@router.post("/account/visitor-login", name="Visitor login")
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


@router.get("/account/info", name="Get User info")
def get_account_info(
    db: Session = Depends(get_db), account_id: str = Depends(get_current_account)
):
    """获取用户信息"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.get_account_info(account_id))


@router.post("/account/settings")
def account_settings_api(
    dto: AccountSettingsDTO,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """用户保存设置"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.save_settings(dto, account_id))

@router.get('/account/settings')
def get_account_settings_api(
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """获取用户设置"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.get_settings(account_id))


@router.post("/account/role", name="Update User role")
def update_role(
    dto: UpdateRoleDTO,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """选择角色"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.update_role_setting(dto, account_id))


@router.get("/account/role", name="Get User role")
def get_account_role(
    db: Session = Depends(get_db), account_id: str = Depends(get_current_account)
):
    """获取选择的角色"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.get_role_setting(account_id))

@router.get("/account/collect")
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


@router.post("/account/collect")
def account_collect_api(
    dto: CollectDTO,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """用户保存单词与句子的接口"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.collect(dto, account_id))


@router.delete("/account/collect")
def account_collect_api(
    dto: CollectDTO,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """取消用户保存的单词或者句子"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.cancel_collect(dto, account_id))


@router.get("/account/collects")
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