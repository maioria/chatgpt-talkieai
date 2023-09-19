import os

from fastapi import APIRouter, Depends, UploadFile, File, Response
from sqlalchemy.orm import Session

from app.config import Config
from app.core import get_current_account
from app.db import get_db
from app.models.response import ApiResponse
from app.services.account_service import AccountService

router = APIRouter()


@router.post("/voice/upload")
def voice_upload_api(
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    account_id: str = Depends(get_current_account),
):
    """上传语音文件"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.voice_upload(file, account_id))


@router.get("/files/{file_name}")
def get_file(file_name: str, response: Response):
    """获取文件"""
    file_path = f"{Config.TEMP_SAVE_FILE_PATH}/{file_name}"
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
