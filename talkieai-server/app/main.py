from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.api.router import router as api_router
from app.config import Config
from app.core.exceptions import UserAccessDeniedException
from app.core.logging import logging
from app.models.response import ApiResponse

app = FastAPI()

# Enables CORS
app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"],
                   )

app.include_router(api_router, prefix=Config.API_PREFIX)


@app.exception_handler(Exception)
async def conflict_error_handler(_, exc: Exception):
    """全局异常处理"""
    logging.error(exc)
    # 返回状态码仍为200，exc的错误信息放到ApiResponse中以json格式方式返回并且可以跨域访问
    return JSONResponse(headers={
        'Access-Control-Allow-Origin': "*",
        'Access-Control-Allow-Methods': "*",
        'Access-Control-Allow-Headers': "*",
    }, content=ApiResponse(code='500', status='FAILED', message=str(exc)).__dict__)


# UserAccessDeniedException异常处理状态码为403
@app.exception_handler(UserAccessDeniedException)
async def user_access_denied_error_handler(_, exc: UserAccessDeniedException):
    """全局异常处理"""
    logging.error(exc)
    # 返回状态码仍为200，exc的错误信息放到ApiResponse中以json格式方式返回并且可以跨域访问
    return JSONResponse(headers={
        'Access-Control-Allow-Origin': "*",
        'Access-Control-Allow-Methods': "*",
        'Access-Control-Allow-Headers': "*",
    }, content=ApiResponse(code='403', status='FAILED', message=str(exc)).__dict__)
