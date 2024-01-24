import json
import os
import re
import datetime

from sqlalchemy.orm import Session

from app.config import Config
from app.core import auth, azure_voice
from app.core.azure_voice import *
from app.core.exceptions import UserAccessDeniedException
from app.core.utils import *
from app.db.sys_entities import *
from app.db.account_entities import *
from app.db.chat_entities import *
from app.models.account_models import *
from app.core.logging import logging
from app.ai import chat_ai
from app.ai.models import *
from app.core.logging import logging
from app.core.language import *
from app.core.language import *


MESSAGE_SYSTEM = "SYSTEM"

class AccountService:
    def __init__(self, db: Session):
        self.db = db

    def visitor_login(self, fingerprint: str, client_host: str, user_agent: str = None):
        """先检查此ip下是否有用户，如果有，直接返回ip下的用户，如果没有，就生成新的访客"""
        visitor = (
            self.db.query(AccountEntity).filter_by(fingerprint=fingerprint).first()
        )
        if not visitor:
            visitor = AccountEntity(
                id=f"visitor_{short_uuid()}",
                fingerprint=fingerprint,
                client_host=client_host,
                user_agent=user_agent,
            )
            self.db.add(visitor)
            self.db.commit()

        self.__check_and_init_default_settings(visitor.id)
        return auth.init_token(visitor.id, visitor.id)

    def collect(self, dto: CollectDTO, account_id: str):
        """用户收藏，根据类型保存到AccountCollectEntity，保存前先做检查，如果已经存在，则不需要再进行保存"""

        # 先检查是否已经存在，如果已经存在，就不需要再进行保存
        if dto.message_id:
            collect = (
                self.db.query(AccountCollectEntity)
                .filter_by(account_id=account_id, message_id=dto.message_id)
                .first()
            )
        else:
            collect = (
                self.db.query(AccountCollectEntity)
                .filter_by(account_id=account_id, type=dto.type, content=dto.content)
                .first()
            )

        if collect:
            if collect.deleted == 1:
                collect.deleted = 0
                collect.update_time = datetime.datetime.now()

            self.db.commit()
            return

        # 查询出session
        if dto.message_id:
            message = (
                self.db.query(MessageEntity)
                .filter_by(id=dto.message_id, account_id=account_id)
                .first()
            )
            content = message.content
        else:
            content = dto.content

        # 获得翻译
        source_language = self.get_account_source_language(account_id)
        translation = chat_ai.invoke_translate(
            TranslateParams(target_language=source_language, content=content)
        )

        # 如果没有任何符号且只有单独一个单词，则type为WORD，否则为 SENTENCE
        if re.match(r"^[a-zA-Z]+$", content) and len(content.split(" ")) == 1:
            type = "WORD"
        else:
            type = "SENTENCE"

        account_collect = AccountCollectEntity(
            account_id=account_id,
            type=type,
            message_id=dto.message_id,
            content=content,
            translation=translation,
        )
        self.db.add(account_collect)

        self.db.commit()
        return

    def get_account_info(self, account_id: str):
        """获取用户的今日聊天次数与总次数返回"""
        # 如果是访客，就返回访客的信息
        if account_id.startswith("visitor_"):
            account = self.db.query(AccountEntity).filter_by(id=account_id).first()
        else:
            # 不再支持account
            raise Exception("不再支持account")
        if not account:
            raise Exception("User not found")
        result = {
            "account_id": account_id,
            "today_chat_count": self.get_user_current_day_system_message_count(
                account_id
            ),
            "total_chat_count": self.get_user_system_message_count(account_id),
        }
        account_settings = (
            self.db.query(AccountSettingsEntity)
            .filter_by(account_id=account_id)
            .first()
        )
        target_language = account_settings.target_language
        result["target_language"] = target_language
        result["target_language_label"] = get_label_by_language(target_language)
        return result

    def get_collect(self, dto: CollectDTO, account_id: str):
        """获取用户是否已经收藏的数据"""
        if dto.message_id:
            collect = (
                self.db.query(AccountCollectEntity)
                .filter_by(account_id=account_id, message_id=dto.message_id)
                .first()
            )
        else:
            collect = (
                self.db.query(AccountCollectEntity)
                .filter_by(account_id=account_id, type=dto.type, content=dto.content)
                .first()
            )
        if collect and collect.deleted == 0:
            return {"is_collect": True}
        else:
            return {"is_collect": False}

    def cancel_collect(self, dto: CollectDTO, account_id: str):
        """取消收藏"""
        if dto.message_id:
            collect = (
                self.db.query(AccountCollectEntity)
                .filter_by(account_id=account_id, message_id=dto.message_id)
                .first()
            )
        else:
            collect = (
                self.db.query(AccountCollectEntity)
                .filter_by(account_id=account_id, type=dto.type, content=dto.content)
                .first()
            )
        if collect:
            collect.deleted = 1
            collect.update_time = datetime.datetime.now()
            self.db.commit()
        return

    def get_collects(self, type: str, page: int, page_size: int, account_id: str):
        """获取用户收藏的列表信息"""
        query = (
            self.db.query(AccountCollectEntity)
            .filter_by(account_id=account_id, type=type, deleted=0)
            .order_by(AccountCollectEntity.create_time.desc())
        )
        collects = query.offset((page - 1) * page_size).limit(page_size).all()
        # 获取总数
        total = query.count()
        result = []
        for collect in collects:
            result.append(
                {
                    "id": collect.id,
                    "type": collect.type,
                    "content": collect.content,
                    "translation": collect.translation,
                    "message_id": collect.message_id,
                    "create_time": date_to_str(collect.create_time),
                }
            )
        return {"total": total, "list": result}

    def get_settings(self, account_id: str):
        """获取AccountSettingsEntity中key 为 auto_playing_voice, playing_voice_speed, auto_text_shadow, auto_pronunciation的配置"""
        settings = (
            self.db.query(AccountSettingsEntity)
            .filter(AccountSettingsEntity.account_id == account_id)
            .first()
        )
        # 设置 vo dict，里面的值与settings中的值一致
        vo = {
            "auto_playing_voice": settings.auto_playing_voice,
            "playing_voice_speed": settings.playing_voice_speed,
            "auto_text_shadow": settings.auto_text_shadow,
            "auto_pronunciation": settings.auto_pronunciation,
            "speech_role_name": settings.speech_role_name,
            "target_language": settings.target_language,
        }

        # 如果存在 speech_role_name，则从azure_voice_configs_group获取对应值，取local_name
        if settings.speech_role_name:
            voice_role_config = get_azure_voice_role_by_short_name(
                settings.speech_role_name
            )
            vo["speech_role_name_label"] = voice_role_config["local_name"]
        return vo

    def save_settings(self, dto: AccountSettingsDTO, account_id: str):
        """保存用户设置"""
        account_settings = (
            self.db.query(AccountSettingsEntity)
            .filter_by(account_id=account_id)
            .first()
        )
        if dto.auto_playing_voice is not None:
            account_settings.auto_playing_voice = dto.auto_playing_voice
        if dto.playing_voice_speed is not None:
            account_settings.playing_voice_speed = dto.playing_voice_speed
        if dto.auto_text_shadow is not None:
            account_settings.auto_text_shadow = dto.auto_text_shadow
        if dto.auto_pronunciation is not None:
            account_settings.auto_pronunciation = dto.auto_pronunciation
        if dto.speech_role_name is not None:
            account_settings.speech_role_name = dto.speech_role_name
        if dto.target_language is not None:
            if dto.target_language != account_settings.target_language:
                # 获取语言对应的语音角色
                speech_role_name = get_azure_language_default_role(
                    dto.target_language
                )
                account_settings.speech_role_name = speech_role_name
            account_settings.target_language = dto.target_language
        self.db.commit()


    def update_role_setting(self, dto: UpdateRoleDTO, account_id: str):
        """选择角色"""
        # 先删除 account_settings 中的数据
        account_settings_entity = (
            self.db.query(AccountSettingsEntity)
            .filter_by(account_id=account_id)
            .first()
        )
        # dto 转json格式保存
        account_settings_entity.role_setting = json.dumps(dto.model_dump())
        self.db.commit()
        return {
            "account_id": account_id,
            "role_name": dto.role_name,
            "role_style": dto.style,
        }

    def get_role_setting(self, account_id: str):
        """获取用户当前设置的角色"""
        # 先删除 account_settings 中的数据
        account_settings_entity = (
            self.db.query(AccountSettingsEntity)
            .filter_by(account_id=account_id)
            .first()
        )
        role_setting = get_azure_voice_role_by_short_name(account_settings_entity.speech_role_name)
        # 补充头像，根据性别补充头像
        if role_setting['gender'] == 1:
            role_setting['role_image'] = 'http://qiniu.prejade.com/1597936949107363840/talkie/images/en-US_JennyNeural.png'
        else:
            role_setting['role_image'] = 'http://qiniu.prejade.com/1597936949107363840/talkie/images/en-US_Guy.png'    
        return {
            "role_setting": role_setting
        }
           

    def get_account_source_language(self, account_id: str):
        """获取用户的学习语言"""
        settings = (
            self.db.query(AccountSettingsEntity)
            .filter_by(account_id=account_id)
            .first()
        )
        if settings:
            return settings.source_language
        else:
            return Config.DEFAULT_SOURCE_LANGUAGE

    def get_account_target_language(self, account_id: str):
        """获取用户的目标语言"""
        settings = (
            self.db.query(AccountSettingsEntity)
            .filter_by(account_id=account_id)
            .first()
        )
        if settings:
            return settings.target_language
        else:
            return Config.DEFAULT_TARGET_LANGUAGE

    def get_user_current_day_system_message_count(self, account_id: str):
        """获取用户当天系统消息次数"""
        # 获取当天0点的时间进行筛选
        today = day_to_str(datetime.datetime.now())
        return (
            self.db.query(MessageEntity)
            .filter_by(account_id=account_id, type=MessageType.SYSTEM.value)
            .filter(MessageEntity.create_time >= today)
            .count()
        )

    def get_user_system_message_count(self, account_id: str):
        """获取用户当天系统消息次数"""
        return (
            self.db.query(MessageEntity)
            .filter_by(account_id=account_id, type=MessageType.SYSTEM.value)
            .count()
        )

    def __check_and_init_default_settings(self, account_id: str):
        """检查并初始化用户的默认设置"""
        # 先检查是否已经存在，如果已经存在，就不需要再进行保存
        settings = (
            self.db.query(AccountSettingsEntity)
            .filter_by(account_id=account_id)
            .first()
        )
        if not settings:
            speech_role_name = get_azure_language_default_role(
                Config.DEFAULT_TARGET_LANGUAGE
            )
            settings = AccountSettingsEntity(
                account_id=account_id,
                target_language=Config.DEFAULT_TARGET_LANGUAGE,
                source_language=Config.DEFAULT_SOURCE_LANGUAGE,
                speech_role_name=speech_role_name,
            )
            self.db.add(settings)
            self.db.commit()
