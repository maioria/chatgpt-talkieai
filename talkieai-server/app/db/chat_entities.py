import datetime

from sqlalchemy import Column, String, DateTime, Integer, Index, Text
from app.db import Base, engine

class MessageSessionEntity(Base):
    """消息会话表"""

    __tablename__ = "message_session"

    id = Column("id", String(80), primary_key=True)
    account_id = Column("account_id", String(80), nullable=False)
    # CHAT TOPIC
    type = Column("type", String(50), nullable=False, default="CHAT")
    message_count = Column("message_count", Integer, default="0")
    is_default = Column("is_default", Integer, default="0")
    completed = Column("completed", Integer, default="0")
    deleted = Column("deleted", Integer, default="0")
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)
    update_time = Column("update_time", DateTime, default=datetime.datetime.now)


class MessageEntity(Base):
    """消息表"""

    __tablename__ = "message"

    id = Column("id", String(80), primary_key=True)
    session_id = Column("session_id", String(80), nullable=False)
    account_id = Column("account_id", String(80), nullable=False)
    sender = Column("sender", String(80), nullable=False)
    receiver = Column("receiver", String(80), nullable=False)
    type = Column("type", String(50), nullable=False)
    content = Column("content", String(2500), nullable=False)
    style = Column("style", String(80), nullable=True)
    length = Column("length", Integer, nullable=False)
    file_name = Column("file_name", String(80), nullable=True)
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)
    deleted = Column("deleted", Integer, default="0")
    # 设置一个自增的sequence 排序使用
    sequence = Column("sequence", Integer, nullable=False)
    # session_id需要加索引
    Index("idx_session_id", "session_id")
    # account_id需要加索引
    Index("idx_account_id", "account_id")
    # sequence 需要加索引
    Index("idx_sequence", "sequence")

class MessageTranslateEntity(Base):
    """用户翻译记录表, 使用自增id"""

    __tablename__ = "message_translate"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    session_id = Column("session_id", String(80), nullable=False)
    message_id = Column("message_id", String(80), nullable=False)
    account_id = Column("account_id", String(80), nullable=False)
    source_language = Column("source_language", String(80), nullable=False)
    target_language = Column("target_language", String(80), nullable=False)
    source_text = Column("source_text", String(512), nullable=False)
    target_text = Column("target_text", String(512), nullable=False)
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)

class MessageGrammarEntity(Base):
    """用户语法与语音分析表，结果使用json保存"""

    __tablename__ = "message_grammar"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    session_id = Column("session_id", String(80), nullable=False)
    message_id = Column("message_id", String(80), nullable=False)
    file_name = Column("file_name", String(80), nullable=True)
    account_id = Column("account_id", String(80), nullable=False)
    # GRAMMAR PRONUNCIATION
    type = Column("type", String(80), nullable=False)
    result = Column("result", Text, nullable=False)
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)

# 数据库未创建表的话自动创建表
Base.metadata.create_all(engine)