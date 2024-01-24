import os
from fastapi import APIRouter, Depends, Request, UploadFile, File, Response
from sqlalchemy.orm import Session
from app.core import get_current_account
from app.db import get_db
from app.models.sys_models import *
from app.models.response import ApiResponse
from app.services.sys_service import SysService
from app.config import Config
from app.core.utils import *

router = APIRouter()

@router.get("/languages/example")
def get_settings_languages_example(
    language: str,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """获取支持的语言"""
    sys_service = SysService(db)
    return ApiResponse(
        data=sys_service.get_settings_languages_example(language, account_id)
    )    
    
# 获取语言下支持的角色
@router.get("/sys/roles")
def get_settings_roles(
    locale: str,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """获取支持的角色"""
    sys_service = SysService(db)
    return ApiResponse(data=sys_service.get_settings_roles(locale, account_id))


@router.get("/sys/languages")
def get_settings_languages(
    db: Session = Depends(get_db), account_id: str = Depends(get_current_account)
):
    """获取支持的语言"""
    sys_service = SysService(db)
    return ApiResponse(data=sys_service.get_settings_languages(account_id))    


@router.post("/voices/upload")
def voice_upload_api(
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    account_id: str = Depends(get_current_account),
):
    """上传语音文件"""
    sys_service = SysService(db)
    return ApiResponse(data=sys_service.voice_upload(file, account_id))


@router.get("/voices/{file_name}")
def get_file(file_name: str, response: Response):
    """获取文件"""
    file_path = voice_file_get_path(file_name)
    # 判断文件是否存在
    if os.path.isfile(file_path):
        with open(file_path, "rb") as file:
            contents = file.read()
            response.headers["Content-Type"] = "application/octet-stream"
            response.headers[
                "Content-Disposition"
            ] = f"attachment; filename={os.path.basename(file_path)}"
            return Response(content=contents, media_type="application/octet-stream")
    else:
        return {"error": f"File {file_name} not found."}

@router.post("/sys/feedback")
def add_feedback(
    dto: FeedbackDTO,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """用户反馈"""
    sys_service = SysService(db)
    sys_service.add_feedback(dto, account_id)
    return ApiResponse(data="SUCCESS")