from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core import get_current_account
from app.db import get_db
from app.models.topic_models import *
from app.models.response import ApiResponse
from app.core.logging import logging
from app.services.topic_service import TopicService

router = APIRouter()


# 用户创建自定义话题
@router.post("/topics/custom", name="Create custom topic")
def create_custom_topic(
    topic: TopicCreateDTO,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """用户创建自定义话题"""
    topic_service = TopicService(db)
    return ApiResponse(data=topic_service.create_custom_topic(topic, account_id))


# 获取用户创建的自定义话题
@router.get("/topics/custom", name="Get custom topic")
def get_custom_topic(
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """获取用户创建的自定义话题"""
    topic_service = TopicService(db)
    return ApiResponse(data=topic_service.get_custom_topic(account_id))

# 获取所有话题组与话题
@router.get("/topics", name="Get all chat topic group")
def get_all_chat_topics(
    type: str,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """获取所有话题组与话题"""
    topic_service = TopicService(db)
    return ApiResponse(data=topic_service.get_all_topics(type, account_id))


# 获取自定义话题的示例
@router.get("/topics/random", name="Get custom topic example")
def get_custom_topic_example(
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """获取自定义话题的示例"""
    topic_service = TopicService(db)
    return ApiResponse(data=topic_service.get_custom_topic_example(account_id))


# 获取话题详情
@router.get("/topics/{topic_id}", name="Get topic detail")
def get_topic_detail(
    topic_id: str,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """获取话题详情"""
    topic_service = TopicService(db)
    return ApiResponse(data=topic_service.get_topic_detail(topic_id, account_id))


# 获取话题历史记录，topic_id做为可选参数，为空时查询所有历史记录
@router.get("/topics/{topic_id}/history", name="Get chat topic history")
def get_chat_topic_history(
    topic_id: str,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """获取话题历史记录，topic_id做为可选参数，为空时查询所有历史记录"""
    topic_service = TopicService(db)
    return ApiResponse(data=topic_service.get_topic_history(topic_id, account_id))


# 获取话题短语记录
@router.get("/topics/{topic_id}/phrases", name="Get chat topic phrases")
def get_chat_topic_phrases(
    topic_id: str,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """获取话题短语记录"""
    topic_service = TopicService(db)
    return ApiResponse(data=topic_service.get_topic_phrases(topic_id, account_id))


# 基于主题创建一个session
@router.post("/topics/{topic_id}/session", name="Create chat topic session")
def create_chat_topic_session(
    topic_id: str,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """基于主题创建一个session"""
    topic_service = TopicService(db)
    return ApiResponse(data=topic_service.create_topic_session(topic_id, account_id))


# 结束当前会话并进行评分
@router.post("/topics/sessions/{session_id}/complete", name="Compete Session")
def complete_session(
    session_id: str,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """结束话题下的session"""
    topic_service = TopicService(db)
    return ApiResponse(
        data=topic_service.complete_topic_session(session_id, account_id)
    )


# 删除当前会话
@router.delete("/topics/{topic_id}/session/{session_id}", name="Delete Session")
def delete_session(
    topic_id: str,
    session_id: str,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """删除话题下的session"""
    topic_service = TopicService(db)
    return ApiResponse(
        data=topic_service.delete_topic_session(topic_id, session_id, account_id)
    )


# 获取话题下的session结果
@router.get(
    "/topics/{topic_id}/session/{session_id}/completion", name="Get Session Result"
)
def get_session_result(
    topic_id: str,
    session_id: str,
    db: Session = Depends(get_db),
    account_id: str = Depends(get_current_account),
):
    """获取话题下的session结果"""
    topic_service = TopicService(db)
    return ApiResponse(
        data=topic_service.get_session_result(topic_id, session_id, account_id)
    )
