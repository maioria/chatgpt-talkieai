import datetime

from sqlalchemy import Column, String, DateTime, Integer, Index, Text
from app.db import Base, engine


class VisitorEntity(Base):
    """访客表"""
    __tablename__ = "visitor"
    id = Column('id', String(80), primary_key=True)
    client_host = Column('client_host', String(50), nullable=False)
    user_agent = Column('user_agent', String(250), nullable=True)
    fingerprint = Column('fingerprint', String(64), nullable=True)
    status = Column('status', String(50), default='ACTIVE')
    create_time = Column('create_time', DateTime, default=datetime.datetime.now)
    update_time = Column('update_time', DateTime, default=datetime.datetime.now)


class AccountPromptEntity(Base):
    """用户提示表"""
    __tablename__ = "account_prompt"
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    session_id = Column('session_id', String(80), nullable=False)
    message_id = Column('message_id', String(80), nullable=False)
    account_id = Column('account_id', String(80), nullable=False)
    prompt_type = Column('prompt_type', String(80), nullable=False)
    source_language = Column('source_language', String(80), nullable=False)
    target_language = Column('target_language', String(80), nullable=False)
    source_text = Column('source_text', String(512), nullable=False)
    target_text = Column('target_text', String(512), nullable=False)
    create_time = Column('create_time', DateTime, default=datetime.datetime.now)
    # account_id需要加索引
    Index('idx_account_id', 'account_id')


class AccountTranslateEntity(Base):
    """用户翻译记录表"""
    __tablename__ = "account_translate"
    id = Column('id', Integer, primary_key=True, autoincrement=True)
    session_id = Column('session_id', String(80), nullable=False)
    message_id = Column('message_id', String(80), nullable=False)
    account_id = Column('account_id', String(80), nullable=False)
    source_language = Column('source_language', String(80), nullable=False)
    target_language = Column('target_language', String(80), nullable=False)
    source_text = Column('source_text', String(512), nullable=False)
    target_text = Column('target_text', String(512), nullable=False)
    create_time = Column('create_time', DateTime, default=datetime.datetime.now)
    # account_id需要加索引
    Index('idx_account_id', 'account_id')


class MessageSessionEntity(Base):
    """消息会话表"""
    __tablename__ = "message_session"

    id = Column('id', String(80), primary_key=True)
    account_id = Column('account_id', String(80), nullable=False)
    name = Column('name', String(80), nullable=True)
    scene = Column('scene', String(80), nullable=True)
    scene_content = Column('scene_content', String(512), nullable=True)
    language = Column('language', String(80), nullable=False)
    # 语音角色
    speech_role_name = Column('speech_role_name', String(80), nullable=False)
    # 性别
    gender = Column('gender', String(35), nullable=False)
    # 语音速度
    speech_rate = Column('speech_rate', String(30), nullable=False)
    # 语音语气
    speech_style = Column('speech_style', String(30), nullable=True)
    # 状态
    status = Column('status', String(50), default='ACTIVE')
    teacher_avatar = Column('teacher_avatar', String(350), nullable=True)
    message_count = Column('message_count', Integer, default='0')
    is_deleted = Column('is_deleted', Integer, default='0')
    create_time = Column('create_time', DateTime, default=datetime.datetime.now)
    update_time = Column('update_time', DateTime, default=datetime.datetime.now)
    # account_id需要加索引
    Index('idx_account_id', 'account_id')


class MessageEntity(Base):
    """消息表"""
    __tablename__ = "message"

    id = Column('id', String(80), primary_key=True)
    account_id = Column('account_id', String(80), nullable=False)
    sender = Column('sender', String(80), nullable=False)
    receiver = Column('receiver', String(80), nullable=False)
    type = Column('type', String(50), nullable=False)
    content = Column('content', String(2500), nullable=False)
    length = Column('length', Integer, nullable=False)
    file_name = Column('file_name', String(80), nullable=True)
    session_id = Column('session_id', String(80), nullable=False)
    is_deleted = Column('is_deleted', Integer, default='0')
    create_time = Column('create_time', DateTime, default=datetime.datetime.now)
    # session_id需要加索引
    Index('idx_session_id', 'session_id')
    # account_id需要加索引
    Index('idx_account_id', 'account_id')


class FileDetail(Base):
    """文件表"""
    __tablename__ = "file_detail"

    id = Column('id', String(80), primary_key=True)
    file_path = Column('file_path', String(150), nullable=False)
    module = Column('module', String(80), nullable=True)
    module_id = Column('module_id', String(80), nullable=True)
    file_name = Column('file_name', String(150), nullable=True)
    file_ext = Column('file_ext', String(20), nullable=True)
    created_by = Column('created_by', String(80), nullable=False)
    create_time = Column('create_time', DateTime, default=datetime.datetime.now)


class SysCacheEntity(Base):
    """系统缓存表"""
    __tablename__ = 'sys_cache'

    id = Column('id', Integer, autoincrement=True, primary_key=True)
    key = Column('key', String(80), nullable=False)
    # value需要使用MEDIUMTEXT格式
    value = Column('value', Text, nullable=False)
    create_time = Column('create_time', DateTime, default=datetime.datetime.now)
    # key需要加索引
    Index('idx_key', 'key')


# 数据库未创建表的话自动创建表
Base.metadata.create_all(engine)
