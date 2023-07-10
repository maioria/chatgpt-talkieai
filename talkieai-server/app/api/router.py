import os

from fastapi import APIRouter, Depends, UploadFile, File, Request, Response
from sqlalchemy.orm import Session

from app.config import Config
from app.core import get_current_account
from app.db import get_db
from app.models.chat_models import VisitorLoginDTO, ChatDTO, TransformSpeechDTO, TranslateDTO, GrammarDTO, \
    PromptDTO, SessionCreateDTO, DemoTranslateDTO, SpeechDemoDTO
from app.models.response import ApiResponse
from app.services.acount_service import AccountService

router = APIRouter()


@router.post("/visitor-login", name="Visitor login")
async def visitor_login(request: Request, dto: VisitorLoginDTO, db: Session = Depends(get_db)):
    """用户访客登录，一个IP只能有一个访客，如果ip已经生成了访客"""
    client_host = request.client.host

    # client_host 不能为空
    if not client_host:
        return ApiResponse(code='400', status='FAILED', message='client_host 不能为空')
    # dto.fingerprint 不能为空
    if not dto.fingerprint:
        return ApiResponse(code='400', status='FAILED', message='dto.fingerprint 不能为空')

    # user_agent不能为空，如果太长，截取最后的250位
    user_agent = request.headers["User-Agent"]
    if not user_agent:
        return ApiResponse(code='400', status='FAILED', message='user_agent 不能为空')
    if len(user_agent) > 250:
        user_agent = user_agent[-250:]

    account_service = AccountService(db)
    return ApiResponse(data=account_service.visitor_login(dto.fingerprint, client_host, user_agent))


@router.get("/user-info", name="Get User info")
async def get_user_info(db: Session = Depends(get_db), account_id: str = Depends(get_current_account)):
    """用户信息"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.get_user_info(account_id))


@router.get("/user-info/usage", name="Get User info usage")
async def get_user_info_usage(db: Session = Depends(get_db), account_id: str = Depends(get_current_account)):
    """用户次数的配置与使用信息"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.get_user_info_usage(account_id))


@router.post("/language-demo-content", name="Translate")
async def language_demo_content(dto: DemoTranslateDTO,
                                db: Session = Depends(get_db),
                                account_id: str = Depends(get_current_account)):
    """根据传入的国家信息翻译成对应的句子返回，前端已经配置好，现在这个接口用不上"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.language_demo_content(dto, account_id))


@router.post("/sessions", name="Create session")
async def create_session(dto: SessionCreateDTO,
                         db: Session = Depends(get_db),
                         account_id: str = Depends(get_current_account)):
    """创建会话"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.create_session(dto, account_id))


@router.delete("/sessions/{session_id}", name="Delete session")
async def delete_session(session_id: str,
                         db: Session = Depends(get_db),
                         account_id: str = Depends(get_current_account)):
    """删除会话"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.delete_session(session_id, account_id))


@router.get("/sessions/count")
async def get_session_count(db: Session = Depends(get_db),
                            account_id: str = Depends(get_current_account)):
    """获取会话数量"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.get_session_count(account_id))


@router.get("/sessions")
async def get_sessions(page: int = 1,
                       page_size: int = 1000,
                       db: Session = Depends(get_db),
                       account_id: str = Depends(get_current_account)):
    """获取会话数据"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.get_session_list(account_id, page, page_size))


@router.get("/sessions/{session_id}")
async def get_session(session_id: str,
                      db: Session = Depends(get_db),
                      account_id: str = Depends(get_current_account)):
    """获取会话详情"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.get_session(session_id, account_id))


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(session_id: str,
                               page: int = 1,
                               page_size: int = 500,
                               db: Session = Depends(get_db),
                               account_id: str = Depends(get_current_account)):
    """获取会话消息"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.get_session_messages(session_id, account_id, page, page_size))


@router.delete("/sessions/{session_id}/messages/latest")
async def delete_latest_session_messages(session_id: str,
                                         db: Session = Depends(get_db),
                                         account_id: str = Depends(get_current_account)):
    """删除最近一次的对话，包含用户的与系统的"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.delete_latest_session_messages(session_id, account_id))


@router.delete("/sessions/{session_id}/messages")
async def delete_all_session_messages(session_id: str,
                                      db: Session = Depends(get_db),
                                      account_id: str = Depends(get_current_account)):
    """删除session下所有的对话"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.delete_all_session_messages(session_id, account_id))


@router.post('/sessions/{session_id}/voice/upload')
async def voice_upload_api(session_id: str,
                           db: Session = Depends(get_db),
                           file: UploadFile = File(...),
                           account_id: str = Depends(get_current_account)):
    """上传语音文件"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.voice_upload(session_id, file, account_id))


@router.post("/chat")
async def chat_api(dto: ChatDTO,
                   db: Session = Depends(get_db),
                   account_id: str = Depends(get_current_account)):
    """发送消息"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.send_message(dto, account_id))


@router.post('/speech')
async def speech_api(dto: TransformSpeechDTO,
                     db: Session = Depends(get_db),
                     account_id: str = Depends(get_current_account)):
    """消息转语音"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.message_speech(dto, account_id))


@router.post("/speech-demo")
async def speech_demo_api(dto: SpeechDemoDTO,
                          db: Session = Depends(get_db),
                          account_id: str = Depends(get_current_account)):
    """语音试听，传入国家信息，通过account_service里面CREATE_SESSION_DEMO_CONTENT转换成语音返回，参数中包含role与rate"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.message_speech_demo(dto, account_id))


@router.post("/translate")
async def translate_api(dto: TranslateDTO,
                        db: Session = Depends(get_db),
                        account_id: str = Depends(get_current_account)):
    """翻译"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.translate(dto, account_id))


@router.post("/grammar")
async def grammar_api(dto: GrammarDTO,
                      db: Session = Depends(get_db),
                      account_id: str = Depends(get_current_account)):
    """分析语法错误"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.grammar_analysis(dto, account_id))


@router.post("/prompt")
async def prompt_api(dto: PromptDTO,
                     db: Session = Depends(get_db),
                     account_id: str = Depends(get_current_account)):
    """帮助用户生成提示句"""
    account_service = AccountService(db)
    return ApiResponse(data=account_service.prompt_sentence(dto, account_id))


@router.get('/files/{file_name}')
async def get_file(file_name: str, response: Response):
    """获取文件，播放语音使用"""
    file_path = f'{Config.TEMP_SAVE_FILE_PATH}/{file_name}'
    # 判断文件是否存在
    if os.path.isfile(file_path):
        with open(file_path, "rb") as file:
            contents = file.read()
            response.headers["Content-Type"] = "application/octet-stream"
            response.headers["Content-Disposition"] = f"attachment; filename={os.path.basename(file_path)}"
            return Response(content=contents, media_type="application/octet-stream")
    else:
        return {"error": f"File {file_name} not found."}
