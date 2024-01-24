import datetime

from sqlalchemy import Column, String, DateTime, Integer, Index, Text
from app.db import Base, engine


# 聊天话题组表
class TopicGroupEntity(Base):
    """聊天话题组表"""

    __tablename__ = "topic_group"

    id = Column("id", String(80), primary_key=True)
    # ROLE_PLAY CHAT_TOPIC
    type = Column("type", String(80), nullable=False)
    name = Column("name", String(80), nullable=False)
    description = Column("description", String(80), nullable=False)
    status = Column("status", String(80), nullable=False, default="ACTIVE")
    sequence = Column("sequence", Integer, nullable=False, default=1)
    created_by = Column("created_by", String(80), nullable=False)
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)
    update_time = Column("update_time", DateTime, default=datetime.datetime.now)


class TopicEntity(Base):
    """聊天话题表"""

    __tablename__ = "topic"

    id = Column("id", String(80), primary_key=True)
    # 所属组
    group_id = Column("group_id", String(80), nullable=False)
    language = Column("language", String(80), nullable=False)
    name = Column("name", String(80), nullable=False)
    level = Column("level", Integer, nullable=False)
    # 所属角色
    role_short_name = Column("role_short_name", String(80), nullable=False)
    # 角色语音默认速度
    role_speech_rate = Column("speech_rate", String(80), nullable=False, default="1")
    topic_bot_name = Column("topic_bot_name", String(580), nullable=False)
    topic_user_name = Column("topic_user_name", String(580), nullable=False)
    prompt = Column("prompt", String(2500), nullable=False)
    description = Column("description", String(580), nullable=False)
    status = Column("status", String(80), nullable=False, default="ACTIVE")
    sequence = Column("sequence", Integer, nullable=False, default=1)
    image_url = Column("image_url", String(500), nullable=True)
    created_by = Column("created_by", String(80), nullable=False)
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)
    update_time = Column("update_time", DateTime, default=datetime.datetime.now)

    # created_by 增加搜索索引
    created_by_index = Index("created_by_index", created_by)
    # group_id 增加搜索索引
    group_id_index = Index("group_id_index", group_id)

class TopicSessionRelation(Base):
    """话题与session关系表"""

    __tablename__ = "topic_session_relation"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    # 所属话题
    topic_id = Column("topic_id", String(80), nullable=False)
    # 所属session_id
    session_id = Column("session_id", String(80), nullable=False)
    account_id = Column("account_id", String(80), nullable=False)
    # 创建时间
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)
    # 更新时间
    update_time = Column("update_time", DateTime, default=datetime.datetime.now)

    # topic_id 增加搜索索引
    topic_id_index = Index("topic_id_index", topic_id)
    # session_id 增加搜索索引
    session_id_index = Index("session_id_index", session_id)    

class AccountTopicEntity(Base):
    """ 用户创建的话题表 """
    
    __tablename__ = "account_topic"

    id = Column("id", String(80), primary_key=True)
    language = Column("language", String(80), nullable=False)
    ai_role = Column("ai_role", String(280), nullable=False)
    my_role = Column("my_role", String(280), nullable=False)
    topic = Column("topic", String(2500), nullable=False)
    account_id = Column("account_id", String(80), nullable=False)
    created_by = Column("created_by", String(80), nullable=False)
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)
    sequence = Column("sequence", Integer, nullable=False, default=1)


# 话题目标表
class TopicTargetEntity(Base):
    """话题目标表"""

    __tablename__ = "topic_target"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    # 所属话题
    topic_id = Column("topic_id", String(80), nullable=False)
    # 目标类型 MAIN TRIAL
    type = Column("type", String(80), nullable=False)
    # 目标描述
    description = Column("description", String(500), nullable=False)
    # 目标描述的翻译
    description_translation = Column("description_translation", String(500), nullable=True)
    # 目标状态
    status = Column("status", String(80), nullable=False, default="ACTIVE")
    sequence = Column("sequence", Integer, nullable=False, default=1)
    created_by = Column("created_by", String(80), nullable=False)
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)
    update_time = Column("update_time", DateTime, default=datetime.datetime.now)

    # topic_id 增加搜索索引
    topic_id_index = Index("topic_id_index", topic_id)

# 话题短语
class TopicPhraseEntity(Base):
    """话题短语"""

    __tablename__ = "topic_phrase"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    # 所属话题
    topic_id = Column("topic_id", String(80), nullable=False)
    # 短语
    phrase = Column("phrase", String(500), nullable=False)
    # 短语翻译
    phrase_translation = Column("phrase_translation", String(500), nullable=True)
    # 短语类型
    type = Column("type", String(80), nullable=False)
    # 短语状态
    status = Column("status", String(80), nullable=False, default="ACTIVE")
    sequence = Column("sequence", Integer, nullable=False, default=1)
    created_by = Column("created_by", String(80), nullable=False)
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)
    update_time = Column("update_time", DateTime, default=datetime.datetime.now)

    # topic_id 增加搜索索引
    topic_id_index = Index("topic_id_index", topic_id)



class TopicHistoryEntity(Base):
    """话题历史记录表"""

    __tablename__ = "topic_history"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    account_id = Column("account_id", String(80), nullable=False)
    # 所属话题
    topic_id = Column("topic_id", String(80), nullable=False)
    # 话题类型
    topic_type = Column("topic_type", String(80), nullable=False)
    # 话题名
    topic_name = Column("topic_name", String(80), nullable=False)
    # 主目标数量
    main_target_count = Column("main_target_count", Integer, nullable=False, default=0)
    # 试验目标数量
    trial_target_count = Column(
        "trial_target_count", Integer, nullable=False, default=0
    )
    main_target_completed_count = Column(
        "main_target_completed_count", Integer, nullable=False, default=0
    )
    trial_target_completed_count = Column(
        "trial_target_completed_count", Integer, nullable=False, default=0
    )
    # 完成度
    completion = Column("completion", Integer, nullable=False, default=0)
    # 语音评分
    audio_score = Column("audio_score", Integer, nullable=True, default=0)
    # 内容评分
    content_score = Column("content_score", Integer, nullable=True, default=0)
    # 建议
    suggestion = Column("suggestion", String(2080), nullable=True)
    word_count = Column("word_count", Integer, nullable=True, default=0)
    # 所属session_id
    session_id = Column("session_id", String(80), nullable=False)
    completed = Column("completed", String(80), nullable=False, default="0")
    status = Column("status", String(80), nullable=False, default="ACTIVE")
    # 创建时间
    create_time = Column("create_time", DateTime, default=datetime.datetime.now)


# 数据库未创建表的话自动创建表
Base.metadata.create_all(engine)
