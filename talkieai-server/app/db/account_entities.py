import datetime

from sqlalchemy import Column, String, DateTime, Integer, Index, Text
from app.db import Base, engine


class AccountEntity(Base):
    """访客表"""

    __tablename__ = "account"

    id = Column("id", String(80), primary_key=True)
    client_host = Column("client_host", String(50), nullable=False)
    user_agent = Column("user_agent", String(512), nullable=True)
    fingerprint = Column("fingerprint", String(64), nullable=True)
    status = Column("status", String(50), default="ACTIVE")
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)
    update_time = Column("update_time", DateTime, default=datetime.datetime.now)

class AccountSettingsEntity(Base):
    """用户设置表"""

    __tablename__ = "account_settings"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    account_id = Column("account_id", String(80), nullable=False)
    source_language = Column("source_language", String(80), nullable=False)
    target_language = Column("target_language", String(80), nullable=False)
    speech_role_name = Column("speech_role_name", String(80), nullable=True)
    auto_playing_voice = Column("auto_playing_voice", Integer, default=1)
    playing_voice_speed = Column("playing_voice_speed", String(50), default='1.0')
    auto_text_shadow = Column("auto_text_shadow", Integer, default=1)
    auto_pronunciation = Column("auto_pronunciation", Integer, default=1)
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)
    update_time = Column("update_time", DateTime, default=datetime.datetime.now)   


class AccountCollectEntity(Base):
    """用户收藏表"""

    __tablename__ = "account_collect"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    message_id = Column("message_id", String(80), nullable=True)
    account_id = Column("account_id", String(80), nullable=False)
    type = Column("type", String(80), nullable=False)
    content = Column("content", String(2500), nullable=True)
    translation = Column("translation", String(2500), nullable=True)
    deleted = Column("deleted", Integer, default="0")
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)
    update_time = Column("update_time", DateTime, default=datetime.datetime.now)
    
# 数据库未创建表的话自动创建表
Base.metadata.create_all(engine)