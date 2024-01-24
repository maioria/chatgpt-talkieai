import datetime

from sqlalchemy import Column, String, DateTime, Integer, Index, Text
from app.db import Base, engine


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

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    locale = Column("locale", String(80), nullable=False)
    local_name = Column("local_name", String(80), nullable=False)
    name = Column("name", String(255), nullable=False)
    short_name = Column("short_name", String(80), nullable=False)
    gender = Column("gender", Integer, nullable=False, default=1)
    # 头像地址
    avatar = Column("avatar", String(350), nullable=True)
    # 试听音频地址
    audio = Column("audio", String(350), nullable=True)
    styles = Column("styles", String(350), nullable=True)
    status = Column("status", String(80), nullable=False, default="ACTIVE")
    # 排序
    sequence = Column("sequence", Integer, nullable=False, default=0)
    # 创建时间
    create_time = Column(
        "create_time", DateTime, nullable=False, default=datetime.datetime.now
    )
    # 更新时间
    update_time = Column(
        "update_time", DateTime, nullable=False, default=datetime.datetime.now
    )
    deleted = Column("deleted", Integer, nullable=False, default=0)



class FileDetail(Base):
    """文件表"""

    __tablename__ = "file_detail"

    id = Column("id", String(80), primary_key=True)
    file_path = Column("file_path", String(150), nullable=False)
    module = Column("module", String(80), nullable=True)
    module_id = Column("module_id", String(80), nullable=True)
    file_name = Column("file_name", String(150), nullable=True)
    file_ext = Column("file_ext", String(20), nullable=True)
    deleted = Column("deleted", Integer, default="0")
    created_by = Column("created_by", String(80), nullable=False)
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)


class SysCacheEntity(Base):
    """系统缓存表"""

    __tablename__ = "sys_cache"
    id = Column("id", Integer, primary_key=True, autoincrement=True)
    key = Column("key", String(80), nullable=False)
    value = Column("value", String(512), nullable=False)
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
    status = Column("status", String(80), nullable=False, default="1")
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)
    update_time = Column("update_time", DateTime, default=datetime.datetime.now)


# 数据库未创建表的话自动创建表
Base.metadata.create_all(engine)
