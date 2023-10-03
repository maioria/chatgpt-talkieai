import datetime

from sqlalchemy import Column, String, DateTime, Integer, Index, Text
from app.db import Base, engine


class AccountEntity(Base):
    """用户表"""

    __tablename__ = "account"

    id = Column("id", String(80), primary_key=True)
    wechat_open_id = Column("wechat_open_id", String(250), nullable=True)
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)
    update_time = Column("update_time", DateTime, default=datetime.datetime.now)


class VisitorEntity(Base):
    """访客表"""

    __tablename__ = "visitor"

    id = Column("id", String(80), primary_key=True)
    client_host = Column("client_host", String(50), nullable=False)
    user_agent = Column("user_agent", String(512), nullable=True)
    fingerprint = Column("fingerprint", String(64), nullable=True)
    status = Column("status", String(50), default="ACTIVE")
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)
    update_time = Column("update_time", DateTime, default=datetime.datetime.now)


class SettingsLanguageEntity(Base):
    """会话语言配置表"""

    __tablename__ = "settings_language"

    id = Column("id", String(80), primary_key=True)
    language = Column("language", String(80), nullable=False)
    full_language = Column("full_language", String(80), nullable=False)
    label = Column("label", String(80), nullable=False)
    full_label = Column("full_label", String(80), nullable=False)
    description = Column("description", String(250), nullable=True)
    sequence = Column("sequence", Integer, default="1")
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)
    update_time = Column("update_time", DateTime, default=datetime.datetime.now)


class SettingsLanguageExampleEntity(Base):
    """会话示例配置表"""

    __tablename__ = "settings_language_example"

    id = Column("id", String(80), primary_key=True)
    language = Column("language", String(80), nullable=False)
    example = Column("example", String(250), nullable=True)
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)
    update_time = Column("update_time", DateTime, default=datetime.datetime.now)


#  会话角色配置表
class SettingsRoleEntity(Base):
    """会话角色配置表"""

    __tablename__ = "settings_role"

    id = Column("id", String(80), primary_key=True)
    language = Column("language", String(80), nullable=False)
    locale = Column("locale", String(80), nullable=False)
    local_name = Column("local_name", String(80), nullable=False)
    name = Column("name", String(255), nullable=False)
    short_name = Column("short_name", String(80), nullable=False)
    # 所属国家
    country = Column("country", String(80), nullable=True)
    country_name = Column("country_name", String(80), nullable=True)
    gender = Column("gender", String(35), nullable=True)
    # 头像地址
    avatar = Column("avatar", String(350), nullable=True)
    # 试听音频地址
    audio = Column("audio", String(350), nullable=True)
    # 排序
    sequence = Column("sequence", Integer, default="0")
    # 创建时间
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)
    # 更新时间
    update_time = Column("update_time", DateTime, default=datetime.datetime.now)


class SettingsRoleStyleEntity(Base):
    """会话角色语气与语音配置表"""

    __tablename__ = "settings_role_style"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    role_name = Column("role_name", String(250), nullable=False)
    style = Column("style", String(80), nullable=False)
    audio = Column("audio", String(350), nullable=True)
    example = Column("example", String(350), nullable=True)
    # 排序
    sequence = Column("sequence", Integer, default="0")
    # 创建时间
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)
    # 更新时间
    update_time = Column("update_time", DateTime, default=datetime.datetime.now)


class MessageSessionEntity(Base):
    """消息会话表"""

    __tablename__ = "message_session"

    id = Column("id", String(80), primary_key=True)
    account_id = Column("account_id", String(80), nullable=False)
    name = Column("name", String(80), nullable=True)
    scene = Column("scene", String(80), nullable=True)
    scene_content = Column("scene_content", String(512), nullable=True)
    language = Column("language", String(80), nullable=False)
    speech_role_name = Column("speech_role_name", String(80), nullable=True)
    gender = Column("gender", String(35), nullable=True)
    # 语音速度
    speech_rate = Column("speech_rate", String(30), nullable=False, default='1.0')
    # 语音语气
    speech_style = Column("speech_style", String(30), nullable=True)
    # 状态
    status = Column("status", String(50), default="ACTIVE")
    teacher_avatar = Column("teacher_avatar", String(350), nullable=True)
    message_count = Column("message_count", Integer, default="0")
    is_default = Column("is_default", Integer, default="0")
    is_deleted = Column("is_deleted", Integer, default="0")
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)
    update_time = Column("update_time", DateTime, default=datetime.datetime.now)


class MessageEntity(Base):
    """消息表"""

    __tablename__ = "message"

    id = Column("id", String(80), primary_key=True)
    account_id = Column("account_id", String(80), nullable=False)
    sender = Column("sender", String(80), nullable=False)
    receiver = Column("receiver", String(80), nullable=False)
    type = Column("type", String(50), nullable=False)
    content = Column("content", String(2500), nullable=False)
    length = Column("length", Integer, nullable=False)
    file_name = Column("file_name", String(80), nullable=True)
    session_id = Column("session_id", String(80), nullable=False)
    is_deleted = Column("is_deleted", Integer, default="0")
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)
    # session_id需要加索引
    Index("idx_session_id", "session_id")
    # account_id需要加索引
    Index("idx_account_id", "account_id")


class FileDetail(Base):
    """文件表"""

    __tablename__ = "file_detail"

    id = Column("id", String(80), primary_key=True)
    file_path = Column("file_path", String(150), nullable=False)
    module = Column("module", String(80), nullable=True)
    module_id = Column("module_id", String(80), nullable=True)
    file_name = Column("file_name", String(150), nullable=True)
    file_ext = Column("file_ext", String(20), nullable=True)
    is_deleted = Column("is_deleted", Integer, default="0")
    created_by = Column("created_by", String(80), nullable=False)
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)


class AccountTranslateEntity(Base):
    """用户翻译记录表, 使用自增id"""

    __tablename__ = "account_translate"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    session_id = Column("session_id", String(80), nullable=False)
    message_id = Column("message_id", String(80), nullable=False)
    account_id = Column("account_id", String(80), nullable=False)
    source_language = Column("source_language", String(80), nullable=False)
    target_language = Column("target_language", String(80), nullable=False)
    source_text = Column("source_text", String(512), nullable=False)
    target_text = Column("target_text", String(512), nullable=False)
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)


class SysCacheEntity(Base):
    """系统缓存表"""

    __tablename__ = "sys_cache"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    key = Column("key", String(80), nullable=False)
    value = Column("value", String(512), nullable=False)
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)
    update_time = Column("update_time", DateTime, default=datetime.datetime.now)


class AccountGrammarEntity(Base):
    """用户语法与语音分析表，结果使用json保存"""

    __tablename__ = "account_grammar"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    session_id = Column("session_id", String(80), nullable=False)
    message_id = Column("message_id", String(80), nullable=False)
    file_name = Column("file_name", String(80), nullable=True)
    account_id = Column("account_id", String(80), nullable=False)
    # GRAMMAR PRONUNCIATION
    type = Column("type", String(80), nullable=False)
    result = Column("result", Text, nullable=False)
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)


class AccountCollectEntity(Base):
    """用户收藏表"""

    __tablename__ = "account_collect"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    session_id = Column("session_id", String(80), nullable=True)
    message_id = Column("message_id", String(80), nullable=True)
    account_id = Column("account_id", String(80), nullable=False)
    type = Column("type", String(80), nullable=False)
    content = Column("content", String(2500), nullable=True)
    translation = Column("translation", String(2500), nullable=True)
    is_deleted = Column("is_deleted", Integer, default="0")
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)
    update_time = Column("update_time", DateTime, default=datetime.datetime.now)


class FeedbackEntity(Base):
    """用户反馈表"""

    __tablename__ = "sys_feedback"

    id = Column("id", Integer, autoincrement=True, primary_key=True)
    account_id = Column("account_id", String(80), nullable=False)
    content = Column("content", String(2500), nullable=False)
    contact = Column("contact", String(250), nullable=False)
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)


class AccountSettingsEntity(Base):
    """用户设置表"""

    __tablename__ = "account_settings"

    id = Column("id", Integer, autoincrement=True, primary_key=True)
    account_id = Column("account_id", String(80), nullable=False)
    key = Column("key", String(80), nullable=False)
    value = Column("value", String(250), nullable=False)
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)
    update_time = Column("update_time", DateTime, default=datetime.datetime.now)

class SysDictTypeEntity(Base):
    """系统字典类型表"""

    __tablename__ = "sys_dict_type"

    id = Column("id", Integer, autoincrement=True, primary_key=True)
    dict_type = Column("dict_type", String(80), nullable=False)
    dict_name = Column("dict_name", String(80), nullable=False)
    status = Column("status", String(80), nullable=False)
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)
    update_time = Column("update_time", DateTime, default=datetime.datetime.now)

class SysDictDataEntity(Base):
    """系统字典数据表"""

    __tablename__ = "sys_dict_data"

    id = Column("id", Integer, autoincrement=True, primary_key=True)
    dict_type = Column("dict_type", String(80), nullable=False)
    dict_label = Column("dict_label", String(80), nullable=False)
    dict_value = Column("dict_value", String(80), nullable=False)
    status = Column("status", String(80), nullable=False, default= "1")
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)
    update_time = Column("update_time", DateTime, default=datetime.datetime.now)

# 数据库未创建表的话自动创建表
Base.metadata.create_all(engine)
