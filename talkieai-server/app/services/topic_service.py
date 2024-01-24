import json

from sqlalchemy.orm import Session
from app.core.utils import *
from app.models.topic_models import *
from app.db.topic_entities import *
from app.db.chat_entities import *
from app.db.account_entities import *
from app.ai.models import *
from app.core.logging import logging
from app.ai import chat_ai
from app.core.azure_voice import *
from app.models.chat_models import *


class TopicService:
    def __init__(self, db: Session):
        self.db = db
        self.__check_and_init_topics()

    def get_topic_greet_params(self, session_id: str) -> TopicGreetParams:
        """获取话题的prompt"""
        # 根据关联关系取到topic_id
        topic_session_relation = (
            self.db.query(TopicSessionRelation).filter_by(session_id=session_id).first()
        )
        topic_entity = (
            self.db.query(TopicEntity)
            .filter(TopicEntity.id == topic_session_relation.topic_id)
            .first()
        )
        topic_greet_params = TopicGreetParams(
            language=topic_entity.language,
            prompt=topic_entity.prompt,
        )
        return topic_greet_params

    def get_topic_message_params(self, session_id: str) -> AITopicMessageParams:
        """获取话题的prompt"""
        # 根据关联关系取到topic_id
        topic_session_relation = (
            self.db.query(TopicSessionRelation).filter_by(session_id=session_id).first()
        )
        topic_entity = (
            self.db.query(TopicEntity)
            .filter(TopicEntity.id == topic_session_relation.topic_id)
            .first()
        )
        styles = []
        if topic_entity.role_short_name:
            voice_role_config = get_azure_voice_role_by_short_name(
                topic_entity.role_short_name
            )
            styles = voice_role_config["style_list"]

        topic_message_params = AITopicMessageParams(
            name=topic_entity.topic_bot_name,
            language=topic_entity.language,
            prompt=topic_entity.prompt,
            speech_role_name=topic_entity.role_short_name,
            styles=styles,
        )
        return topic_message_params

    def get_all_topics(self, type: str, account_id: str):
        """获取所有话题组与话题"""

        # 获取用户配置，通过用户配置获取language
        account_settins = (
            self.db.query(AccountSettingsEntity)
            .filter(AccountSettingsEntity.account_id == account_id)
            .first()
        )
        # 如果用户没有配置，则使用默认的en-US
        if account_settins is None:
            language = "en-US"
        else:
            language = account_settins.target_language
            if language == "en-GB":
                language = "en-US"

        result = []
        topic_group_entities = (
            self.db.query(TopicGroupEntity)
            .filter(
                TopicGroupEntity.type == type,
                TopicEntity.language == language,
            )
            .order_by(TopicGroupEntity.sequence.desc())
            .all()
        )
        # 迭代话题组，获取话题组下的话题
        for topic_group_entity in topic_group_entities:
            topic_entities = (
                self.db.query(TopicEntity)
                .filter(TopicEntity.group_id == topic_group_entity.id)
                .order_by(TopicEntity.sequence.desc())
                .all()
            )

            # 批量查询话题是否已经完成的状态，在后续迭代中补充此属性
            topic_ids = []
            for topic_entity in topic_entities:
                topic_ids.append(topic_entity.id)
            topic_history_entities = (
                self.db.query(TopicHistoryEntity)
                .filter(TopicHistoryEntity.topic_id.in_(topic_ids))
                .filter(TopicHistoryEntity.account_id == account_id)
                .filter(TopicHistoryEntity.completed == "1")
                .all()
            )
            topic_history_map = {}
            for topic_history_entity in topic_history_entities:
                topic_history_map[topic_history_entity.topic_id] = topic_history_entity

            # 迭代话题数据进行补充
            topics = []
            for topic_entitity in topic_entities:
                topic = {
                    "id": topic_entitity.id,
                    "name": topic_entitity.name,
                    "description": topic_entitity.description,
                    "prompt": topic_entitity.prompt,
                    "level": topic_entitity.level,
                    "image_url": topic_entitity.image_url,
                }

                # 补充是否已经完成的状态
                if topic_entitity.id in topic_history_map:
                    topic["completed"] = topic_history_map[topic_entitity.id].completed
                else:
                    topic["completed"] = "0"

                topics.append(topic)
            group = {
                "id": topic_group_entity.id,
                "name": topic_group_entity.name,
                "topics": topics,
            }
            result.append(group)
        return result

    def get_topic_detail(self, topic_id: str, account_id: str):
        """获取话题详情"""
        topic_entity = (
            self.db.query(TopicEntity).filter(TopicEntity.id == topic_id).first()
        )
        # 获取话题目标
        topic_target_entities = (
            self.db.query(TopicTargetEntity)
            .filter(TopicTargetEntity.topic_id == topic_id)
            .order_by(TopicTargetEntity.type)
            .all()
        )
        # 迭代话题目标数据进行补充
        # TopicTargetEntity按 type为 MAIN TRIAL 的不同值进行组装
        main_targets = []
        trial_targets = []
        for topic_target_entity in topic_target_entities:
            target = {
                "id": topic_target_entity.id,
                "type": topic_target_entity.type,
                "description": topic_target_entity.description,
            }
            if topic_target_entity.type == "MAIN":
                main_targets.append(target)
            elif topic_target_entity.type == "TRIAL":
                trial_targets.append(target)

        result = {
            "id": topic_entity.id,
            "name": topic_entity.name,
            "description": topic_entity.description,
            "prompt": topic_entity.prompt,
            "image_url": topic_entity.image_url,
            "main_targets": main_targets,
            "trial_targets": trial_targets,
        }
        return result

    def create_topic_session(self, topic_id: str, account_id: str):
        """基于主题创建一个会话"""
        # 获取Topic详情
        topic_entity = (
            self.db.query(TopicEntity).filter(TopicEntity.id == topic_id).first()
        )

        # 创建session
        session = MessageSessionEntity(
            id=f"session_{short_uuid()}",
            account_id=account_id,
            type="TOPIC",
        )
        self.db.add(session)

        # 创建session与topic的关系
        session_topic_relation = TopicSessionRelation(
            session_id=session.id,
            topic_id=topic_id,
            account_id=account_id,
        )
        self.db.add(session_topic_relation)

        # 保存话题历史记录
        topic_entity = (
            self.db.query(TopicEntity).filter(TopicEntity.id == topic_id).first()
        )
        topic_history_entity = TopicHistoryEntity(
            account_id=account_id,
            topic_id=topic_id,
            topic_type="TOPIC",
            topic_name=topic_entity.name,
            completion=0,
            session_id=session.id,
        )
        self.db.add(topic_history_entity)

        self.db.commit()
        return {"id": session.id}

    def complete_topic_session(self, session_id: str, account_id: str):
        """结束话题下的session"""
        # 获取话题与session数据
        topic_session_relation = (
            self.db.query(TopicSessionRelation).filter_by(session_id=session_id).first()
        )
        topic_id = topic_session_relation.topic_id
        topic_entity = (
            self.db.query(TopicEntity).filter(TopicEntity.id == topic_id).first()
        )
        session_entity = (
            self.db.query(MessageSessionEntity)
            .filter(MessageSessionEntity.id == session_id)
            .first()
        )
        # 取出所有的聊天内容，通过AI进行完成度与评分计算，并计算出所使用的单词数量
        message_entities = (
            self.db.query(MessageEntity)
            .filter(MessageEntity.session_id == session_id)
            .order_by(MessageEntity.create_time.asc())
            .all()
        )
        messages = []
        for message in message_entities:
            if message.type == MessageType.SYSTEM.value:
                messages.append(MessageItemParams(role='assistant', content=message.content))
            else:
                messages.append(MessageItemParams(role='user', content=message.content))

        # 计算完成度，取出topic下所有的target
        topic_target_entities = (
            self.db.query(TopicTargetEntity)
            .filter(TopicTargetEntity.topic_id == topic_id)
            .all()
        )
        targets = []
        for target in topic_target_entities:
            targets.append(target.description)
        invoke_result = chat_ai.topic_invoke_complete(
            AITopicCompleteParams(
                language=topic_entity.language, messages=messages, targets=targets
            )
        )
        # 获取history 并进行记录
        topic_history_entity = (
            self.db.query(TopicHistoryEntity)
            .filter(TopicHistoryEntity.session_id == session_id)
            .first()
        )
        topic_history_entity.completion = invoke_result.targets
        topic_history_entity.content_score = invoke_result.score
        topic_history_entity.word_count = invoke_result.words
        topic_history_entity.suggestion = invoke_result.suggestion
        topic_history_entity.completed = "1"

        session_entity.completed = "1"
        self.db.commit()

    def delete_topic_session(self, topic_id: str, session_id: str, account_id: str):
        """把话题下的history的status设置为DELETED"""
        topic_history_entity = (
            self.db.query(TopicHistoryEntity)
            .filter(TopicHistoryEntity.session_id == session_id)
            .first()
        )
        topic_history_entity.status = "DELETED"
        self.db.commit()

    def get_custom_topic_example(self, account_id: str):
        """获取随机话题"""
        return {"my_role": "Jack", "ai_role": "小厨师", "topic": "关于厨房的那些事儿"}

    def create_custom_topic(self, dto: TopicCreateDTO, account_id: str):
        """用户创建自己的话题"""
        # 获取用户的语言配置信息
        account_settins = (
            self.db.query(AccountSettingsEntity)
            .filter(AccountSettingsEntity.account_id == account_id)
            .first()
        )
        language = account_settins.target_language
        if language == "en-GB":
            language = "en-US"
        account_topic = AccountTopicEntity(
            id=f"account_topic_{short_uuid()}",
            account_id=account_id,
            language=language,
            ai_role=dto.ai_role,
            my_role=dto.my_role,
            topic=dto.topic,
        )
        return account_topic.id

    def get_custom_topic(self, account_id: str):
        """获取用户创建的自定义话题"""
        account_topics = (
            self.db.query(AccountTopicEntity)
            .filter(AccountTopicEntity.account_id == account_id)
            .all()
        )
        result = []
        for account_topic in account_topics:
            result.append(
                {
                    "id": account_topic.id,
                    "ai_role": account_topic.ai_role,
                    "my_role": account_topic.my_role,
                    "topic": account_topic.topic,
                }
            )
        return result

    def get_session_result(self, topic_id: str, session_id: str, account_id: str):
        """获取主题聊天下的结果"""
        topic_history_entity = (
            self.db.query(TopicHistoryEntity)
            .filter(TopicHistoryEntity.session_id == session_id)
            .first()
        )
        return {
            "topic_name": topic_history_entity.topic_name,
            "main_target_count": topic_history_entity.main_target_count,
            "trial_target_count": topic_history_entity.trial_target_count,
            "main_target_completed_count": topic_history_entity.main_target_completed_count,
            "trial_target_completed_count": topic_history_entity.trial_target_completed_count,
            "completion": topic_history_entity.completion,
            "audio_score": topic_history_entity.audio_score,
            "content_score": topic_history_entity.content_score,
            "suggestion": topic_history_entity.suggestion,
            "word_count": topic_history_entity.word_count,
        }

    def get_topic_history(self, topic_id: str, account_id: str):
        """获取话题历史记录，topic_id做为可选参数，为空时查询所有历史记录"""
        result = []
        if topic_id is None:
            topic_history_entities = (
                self.db.query(TopicHistoryEntity)
                .filter(
                    TopicHistoryEntity.account_id == account_id,
                    TopicHistoryEntity.status == "ACTIVE",
                )
                .order_by(TopicHistoryEntity.create_time.desc())
                .all()
            )
        else:
            topic_history_entities = (
                self.db.query(TopicHistoryEntity)
                .filter(TopicHistoryEntity.account_id == account_id)
                .filter(
                    TopicHistoryEntity.topic_id == topic_id,
                    TopicHistoryEntity.status == "ACTIVE",
                )
                .order_by(TopicHistoryEntity.create_time.desc())
                .all()
            )

        # 查出来所有历史记录涉及的Topic, 后面迭代进行补充
        topic_ids = []
        for topic_history_entity in topic_history_entities:
            topic_ids.append(topic_history_entity.topic_id)
        topic_entities = (
            self.db.query(TopicEntity).filter(TopicEntity.id.in_(topic_ids)).all()
        )
        # 迭代话题历史记录数据进行补充
        for topic_history_entity in topic_history_entities:
            topic_id = topic_history_entity.topic_id
            # 通过topic_entities取出对应的topic
            topic_entity = next(filter(lambda x: x.id == topic_id, topic_entities))
            create_time_str = date_to_str(topic_history_entity.create_time)
            history = {
                "id": topic_history_entity.id,
                "topic_id": topic_history_entity.topic_id,
                "topic_type": topic_history_entity.topic_type,
                "topic_name": topic_history_entity.topic_name,
                "completion": topic_history_entity.completion,
                "session_id": topic_history_entity.session_id,
                "create_time": create_time_str,
                "create_time_friendly": friendly_time(create_time_str),
                "completed": topic_history_entity.completed,
                "topic": {
                    "id": topic_entity.id,
                    "topic": topic_entity.name,
                    "description": topic_entity.description,
                    "prompt": topic_entity.prompt,
                    "image_url": topic_entity.image_url,
                },
            }
            result.append(history)

        return result

    def get_topic_phrases(self, topic_id: str, account_id: str):
        """获取话题短语记录"""
        result = []
        topic_phrase_entities = (
            self.db.query(TopicPhraseEntity)
            .filter(TopicPhraseEntity.topic_id == topic_id)
            .order_by(TopicPhraseEntity.sequence)
            .all()
        )
        for topic_phrase_entity in topic_phrase_entities:
            phrase = {
                "id": topic_phrase_entity.id,
                "phrase": topic_phrase_entity.phrase,
                "phrase_translation": topic_phrase_entity.phrase_translation,
                "type": topic_phrase_entity.type,
                "sequence": topic_phrase_entity.sequence,
            }
            result.append(phrase)
        return result

    def __check_and_init_topics(self):
        """检查与生成默认的 topics"""
        # 检查topic_group是否有数据
        topic_group_entities = self.db.query(TopicGroupEntity).all()
        if len(topic_group_entities) != 0:
            return

        # 根据配置文件生成默认数据
        with open("data/default_topic_data.json", "r") as f:
            topic_data = json.load(f)

        default_account = "system_init"
        for topic_group in topic_data["groups"]:
            topic_group_entity = TopicGroupEntity(
                id=topic_group["id"],
                type=topic_group["type"],
                name=topic_group["name"],
                sequence=topic_group["sequence"],
                description=topic_group["description"],
                created_by=default_account,
            )
            self.db.add(topic_group_entity)

            for topic in topic_group["topics"]:
                topic_entity = TopicEntity(
                    id=topic["id"],
                    group_id=topic_group_entity.id,
                    name=topic["name"],
                    description=topic["description"],
                    level=topic["level"],
                    image_url=topic["image_url"],
                    language=topic["language"],
                    role_short_name=topic["role_short_name"],
                    role_speech_rate=topic["role_speech_rate"],
                    sequence=topic["sequence"],
                    topic_user_name=topic["topic_user_name"],
                    topic_bot_name=topic["topic_bot_name"],
                    prompt=topic["prompt"],
                    created_by=default_account,
                )
                self.db.add(topic_entity)
                for target in topic["targets"]:
                    topic_target_entity = TopicTargetEntity(
                        topic_id=topic_entity.id,
                        type=target["type"],
                        description=target["description"],
                        sequence=target["sequence"],
                        description_translation=target["description_translation"],
                        created_by=default_account,
                    )
                    self.db.add(topic_target_entity)

                for phrase in topic["phrases"]:
                    topic_phrase_entity = TopicPhraseEntity(
                        topic_id=topic_entity.id,
                        phrase=phrase["phrase"],
                        phrase_translation=phrase["phrase_translation"],
                        type=phrase["type"],
                        sequence=phrase["sequence"],
                        created_by=default_account,
                    )
                    self.db.add(topic_phrase_entity)
        self.db.commit()
