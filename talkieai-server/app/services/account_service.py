import hashlib
import json
import os
import re
from datetime import datetime
from typing import List, Dict

from fastapi import UploadFile
from string import Template
from sqlalchemy.orm import Session

from pydub import AudioSegment
from app.config import Config
from app.core import wechat_component, auth, azure_voice
from app.core.azure_voice import speech_translate_text, speech_translate_text_compress, speech, speech_by_ssml
from app.core.exceptions import UserAccessDeniedException
from app.core.utils import (
    short_uuid,
    date_to_str,
    friendly_time,
    day_to_str,
    save_file,
    file_get_path,
    get_date_str,
)
from app.db.entities import (
    AccountEntity,
    VisitorEntity,
    MessageSessionEntity,
    MessageEntity,
    FileDetail,
    AccountTranslateEntity,
    AccountGrammarEntity,
    SysCacheEntity,
    AccountCollectEntity,
    SettingsLanguageEntity,
    SettingsRoleEntity,
    FeedbackEntity,
    AccountSettingsEntity,
    SettingsRoleStyleEntity,
    SettingsLanguageExampleEntity,
)
from app.models.account_models import (
    WechatLoginDTO,
    MessageType,
    ChatDTO,
    TransformSpeechDTO,
    VoiceTranslateDTO,
    TranslateDTO,
    TransformContentSpeechDTO,
    GrammarDTO,
    PronunciationDTO,
    WordDetailDTO,
    CollectDTO,
    PromptDTO,
    TranslateTextDTO,
    FeedbackDTO,
    AccountSettingsDTO,
    WordPracticeDTO,
    MessagePracticeDTO,
    CreateSessionDTO,
)
from app.core.chat_gpt import ApiKeyModel, ChatGPTInvokeDTO, ChatGptRemoteComponent
from app.core.logging import logging

MESSAGE_SYSTEM = "SYSTEM"
ACCOUNT_SETTINGS_AUTO_PLAYING_VOICE = "auto_playing_voice"
ACCOUNT_SETTINGS_PLAYING_VOICE_SPEED = "playing_voice_speed"
ACCOUNT_SETTINGS_AUTO_TEXT_SHADOW = "auto_text_shadow"
ACCOUNT_SETTINGS_AUTO_PRONUNCIATION = "auto_pronunciation"
chat_gpt_component = ChatGptLocalComponent()


class AccountService:
    def __init__(self, db: Session):
        self.db = db

    def wechat_login(self, dto: WechatLoginDTO):
        """微信登录，通过code获取用户的信息实现登录"""
        wechat_data = wechat_component.get_user_info(dto.code)
        # 获取openid后，如果数据库中的wechat_user表没有此用户，就创建用户，如果有此用户，就更新用户的信息
        wechat_user = (
            self.db.query(AccountEntity)
            .filter_by(wechat_open_id=wechat_data["openid"])
            .first()
        )
        if not wechat_user:
            # 创建用户
            wechat_user = AccountEntity(
                id=f"wechat_{short_uuid()}", wechat_open_id=wechat_data["openid"]
            )
            self.db.add(wechat_user)
            self.db.commit()
        return auth.init_token(wechat_user.id, wechat_user.id)

    def visitor_login(self, fingerprint: str, client_host: str, user_agent: str = None):
        """先检查此ip下是否有用户，如果有，直接返回ip下的用户，如果没有，就生成新的访客"""
        visitor = (
            self.db.query(VisitorEntity).filter_by(fingerprint=fingerprint).first()
        )
        if not visitor:
            visitor = VisitorEntity(
                id=f"visitor_{short_uuid()}",
                fingerprint=fingerprint,
                client_host=client_host,
                user_agent=user_agent,
            )
            self.db.add(visitor)
            self.db.commit()
        return auth.init_token(visitor.id, visitor.id)

    def get_account_info(self, account_id: str):
        """获取用户的今日聊天次数与总次数返回"""
        # 如果是访客，就返回访客的信息
        if account_id.startswith("visitor_"):
            account = self.db.query(VisitorEntity).filter_by(id=account_id).first()
        else:
            account = self.db.query(AccountEntity).filter_by(id=account_id).first()
        if not account:
            raise Exception("User not found")
        return {
            "account_id": account_id,
            "today_chat_count": self.get_user_current_day_system_message_count(
                account_id
            ),
            "total_chat_count": self.get_user_system_message_count(account_id),
        }

    def get_user_current_day_system_message_count(self, account_id: str):
        """获取用户当天系统消息次数"""
        # 获取当天0点的时间进行筛选
        today = day_to_str(datetime.now())
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

    def get_settings_languages_example(self, language: str, account_id: str):
        """获取语言下的示例"""
        # 获取语言下的示例
        # 语言没有国家  所以去掉后面的国家后缀
        language = language.split("-")[0]
        languages = (
            self.db.query(SettingsLanguageExampleEntity)
            .filter_by(language=language)
            .first()
        )
        return languages.example

    def get_settings_languages(self, account_id: str):
        """根据语言配置实体SettingsLanguageEntity获取应用支持的语言，语言根据language字段去重"""
        languages = (
            self.db.query(SettingsLanguageEntity)
            .distinct(SettingsLanguageEntity.language)
            .order_by(SettingsLanguageEntity.sequence.asc())
            .all()
        )
        print([language.language for language in languages])
        result = []
        for language in languages:
            result.append(
                {
                    "id": language.id,
                    "language": language.language,
                    "label": language.label,
                    "full_label": language.full_label,
                }
            )
        return result

    def get_settings_roles(self, locale: str, account_id: str):
        """根据语言获取语言下所有支持的角色"""
        roles = (
            self.db.query(SettingsRoleEntity)
            .filter_by(locale=locale)
            .order_by(SettingsRoleEntity.name.asc())
            .all()
        )
        result = []
        # 通过roles批量获取所有的style，并且在迭代中进行组装
        role_names = [role.short_name for role in roles]
        styles = (
            self.db.query(SettingsRoleStyleEntity)
            .filter(SettingsRoleStyleEntity.role_name.in_(role_names))
            .all()
        )
        for role in roles:
            # 根据role_name获取style
            role_styles = [
                style.style for style in styles if style.role_name == role.short_name
            ]
            result.append(
                {
                    "id": role.id,
                    "country": role.country,
                    "name": role.name,
                    "locale": role.locale,
                    "local_name": role.local_name,
                    "short_name": role.short_name,
                    "avatar": role.avatar,
                    "audio": role.audio,
                    "speech_content": "",
                    "role_styles": role_styles,
                }
            )
        return result

    def create_session(self, dto: CreateSessionDTO, account_id: str):
        """为用户创建新的session，并且设置成默认的session"""
        # 根据role_name获取settings_role信息
        role = (
            self.db.query(SettingsRoleEntity)
            .filter_by(short_name=dto.role_name)
            .first()
        )
        # 根据SettingsRoleStyleEntity来获取role下第一个style，如果没有style则使用""
        style = (
            self.db.query(SettingsRoleStyleEntity)
            .filter_by(role_name=role.short_name)
            .order_by(SettingsRoleStyleEntity.sequence.asc())
            .first()
        )
        if style:
            role_style = style.style
        else:
            role_style = ""
        # 根据参数创建MessageSessionEntity
        session = MessageSessionEntity(
            id=f"session_{short_uuid()}",
            account_id=account_id,
            is_default=1,
            gender=role.gender,
            teacher_avatar=role.avatar,
            name=role.local_name,
            language=role.locale,
            scene=None,
            scene_content=None,
            speech_role_name=role.short_name,
            speech_rate="1.0",
            speech_style=role_style,
        )
        self.db.add(session)
        self.db.commit()
        return self.__convert_session_model(session)

    def get_default_session(self, account_id: str):
        """获取用户的默认会话, 如果没有默认会话，就创建一个"""
        session = (
            self.db.query(MessageSessionEntity)
            .filter_by(account_id=account_id, is_default=1)
            .order_by(MessageSessionEntity.create_time.desc())
            .first()
        )
        if not session:
            return None
        return self.__convert_session_model(session)

    def get_session(self, session_id, account_id: str):
        """获取message_session详情"""
        session = (
            self.db.query(MessageSessionEntity)
            .filter_by(account_id=account_id, id=session_id, is_deleted=0)
            .first()
        )
        if session is None:
            raise Exception("会话不存在")
        result = self.__convert_session_model(session)
        # 获取会话下的消息
        result["messages"] = self.get_session_messages(session_id, account_id, 1, 100)
        return result

    def get_session_messages(
        self, session_id: str, account_id: str, page: int, page_size: int
    ):
        query = self.db.query(MessageEntity).filter_by(
            session_id=session_id, account_id=account_id, is_deleted=0
        )
        messages = (
            query.order_by(MessageEntity.create_time.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        # 获取总数
        total = query.count()
        result = []
        for message in reversed(messages):
            result.append(self.initMessageResult(message))
        return {"total": total, "list": result}

    def initMessageResult(self, message: MessageEntity):
        return {
            "role": "ASSISTANT" if message.type == MessageType.SYSTEM.value else "USER",
            "content": message.content,
            "file_name": message.file_name,
            "id": message.id,
            "create_time": date_to_str(message.create_time),
            "session_id": message.session_id,
        }

    def voice_upload(self, file: UploadFile, account_id: str):
        """获取用户当天使用的语音数量，如果超过了配置数量则抛出错误"""
        file_name = save_file(file)
        # 如果上传的是mp3格式(暂时只有android手机只能用mp3格式), 就转换成wav返回, 为了后续azure服务解析音频(mp3会解析失败), 因为chat接口本身比较慢，所以在这里进行转换
        if file.filename.endswith(".mp3"):
            mp3_file_path = file_get_path(file_name)
            print(mp3_file_path)
            wav_file_name = file_name.replace(".mp3", ".wav")
            wav_file_path = file_get_path(wav_file_name)
            print(wav_file_path)
            sound = AudioSegment.from_mp3(mp3_file_path)
            sound.export(wav_file_path, format="wav")
            # mp3文件需要删除
            os.remove(mp3_file_path)
            file_name = wav_file_name
        return {"file": file_name}

    def transform_text(self, session_id: str, dto: VoiceTranslateDTO, account_id: str):
        """语音解析成文字"""
        session = (
            self.db.query(MessageSessionEntity)
            .filter_by(id=session_id, account_id=account_id)
            .first()
        )
        result = speech_translate_text(
            f"{Config.TEMP_SAVE_FILE_PATH}/{dto.file_name}", session.language
        )
        return result

    def message_practice(
        self, message_id: str, dto: MessagePracticeDTO, account_id: str
    ):
        """用户发送过的消息进行练习"""
        message = self.db.query(MessageEntity).filter_by(id=message_id).first()
        if not message:
            raise Exception("Message not found")
        # 获取message_session
        session = (
            self.db.query(MessageSessionEntity).filter_by(id=message.session_id).first()
        )
        return azure_voice.speech_pronunciation(
            message.content, file_get_path(dto.file_name), session.language
        )

    def get_session_greeting(self, session_id: str, account_id: str):
        """需要会话没有任何消息时，需要返回的问候语"""
        # 获取会话下的消息
        messages = (
            self.db.query(MessageEntity)
            .filter_by(session_id=session_id, account_id=account_id, is_deleted=0)
            .order_by(MessageEntity.create_time.desc())
            .slice(0, 1)
            .all()
        )
        if len(messages) == 1:
            raise Exception("Session has messages")
        # 根据message查询到session
        session = (
            self.db.query(MessageSessionEntity)
            .filter_by(id=session_id, account_id=account_id)
            .first()
        )
        messages = [
            {
                "role": "system",
                "content": "You need to greet with "
                + session.language
                + " Simplified.",
            }
        ]
        result = self.__invoke_chat(messages)
        add_message = self.__add_system_message(session_id, account_id, result)
        return self.initMessageResult(add_message)

    def send_session_message(self, session_id: str, dto: ChatDTO, account_id: str):
        """发送消息"""
        # 查询到session
        session = (
            self.db.query(MessageSessionEntity)
            .filter_by(id=session_id, account_id=account_id)
            .first()
        )

        # 如果有file_name却没有message，需要解析出message
        if not dto.file_name and not dto.message:
            raise Exception("Message or file_name is required")
        if dto.message:
            send_message_content = dto.message
        else:
            send_message_content = speech_translate_text(
                f"{Config.TEMP_SAVE_FILE_PATH}/{dto.file_name}", session.language
            )
            if not send_message_content:
                raise Exception("Can not recognize the voice")

        send_message = self.__add_account_message(
            account_id, session_id, send_message_content, dto.file_name
        )
        send_message_id = send_message.id
        base_template_str = "I want you to act as an $language speaking partner and improver, your name is $name. No matter what language I speak to you, you need to reply me in $language. I hope you keep your responses clean and limit your responses to 80 characters. I hope you will ask me a question from time to time in your reply. Now let's start practicing. Remember, I want you reply me in $language and your name is $name and do not respond with any other information about yourself."
        if session.speech_style:
            base_template_str = (
                base_template_str
                + " I want you to keep your tone "
                + session.speech_style
                + "."
            )
        system_content_template = Template(base_template_str)
        params = {"language": session.language, "name": "Talkie"}
        system_content = system_content_template.substitute(params)
        messages = [{"role": "system", "content": system_content}]
        message_history = (
            self.db.query(MessageEntity)
            .filter(MessageEntity.session_id == session_id)
            .order_by(MessageEntity.create_time.desc())
            .slice(0, 6)
            .all()
        )
        for message in reversed(message_history):
            if message.type == MessageType.SYSTEM.value:
                messages.append({"role": "assistant", "content": message.content})
            else:
                messages.append({"role": "user", "content": message.content})

        invoke_result = self.__invoke_chat(messages)
        add_message = self.__add_system_message(session_id, account_id, invoke_result)
        return {
            "data": invoke_result,
            "id": add_message.id,
            "session_id": session_id,
            "send_message_id": send_message_id,
            "send_message_content": send_message_content,
            "create_time": date_to_str(add_message.create_time),
        }

    def message_speech(self, dto: TransformSpeechDTO, account_id: str):
        """文字转语音"""
        # 如果没有，就生成一个
        message = self.db.query(MessageEntity).filter_by(id=dto.message_id).first()
        # 获取信息对应的message_session信息，获取对应的配置

        speech_rate_setting = self.get_setting(
            account_id, ACCOUNT_SETTINGS_PLAYING_VOICE_SPEED
        )

        speech_rate = "1.0"
        if speech_rate_setting:
            if speech_rate_setting == "0":
                speech_rate = "0.5"
            elif speech_rate_setting == "2":
                speech_rate = "1.5"

        filename = f"{message.id}_{speech_rate}.wav"

        file_detail = (
            self.db.query(FileDetail)
            .filter(
                FileDetail.module == "SPEECH_VOICE",
                FileDetail.file_name == filename,
            )
            .order_by(FileDetail.create_time.desc())
            .first()
        )
        if not file_detail:
            session = (
                self.db.query(MessageSessionEntity)
                .filter_by(id=message.session_id)
                .first()
            )
            full_file_name = f"{Config.TEMP_SAVE_FILE_PATH}/{filename}"

            # 如果speech_rate为NORMAL并且feel是NEUTRAL，则使用speech直接转换，否则使用speech_by_ssml转换
            if speech_rate == "1.0":
                speech(
                    message.content, full_file_name, voice_name=session.speech_role_name
                )
            else:
                speech_by_ssml(
                    message.content,
                    full_file_name,
                    voice_name=session.speech_role_name,
                    speech_rate=speech_rate,
                    feel=session.speech_style,
                    targetLang=session.language,
                )
            file_detail = FileDetail(
                id=short_uuid(),
                file_path=filename,
                module="SPEECH_VOICE",
                file_name=filename,
                module_id=dto.message_id,
                file_ext="wav",
                created_by=account_id,
            )
            self.db.add(file_detail)
            message.file_name = filename
            self.db.commit()
            self.db.flush()
        return {"file": file_detail.file_name}

    def translate_text(self, dto: TranslateTextDTO, account_id: str):
        """翻译"""
        if dto.session_id:
            # 如果有session_id，就根据session_id获取message_session的language
            message_session = (
                self.db.query(MessageSessionEntity).filter_by(id=dto.session_id).first()
            )
            target_language = message_session.language
        else:
            target_language = dto.target_language
        messages = [
            {
                "role": "system",
                "content": "You are a translation engine that can only translate text and cannot interpret it, ensuring that the translation is clear, concise, and coherent.",
            },
            {
                "role": "user",
                "content": f"Please translate the following text into {target_language} Simplified: {dto.text}",
            },
        ]
        result = self.__invoke_chat(messages)
        return result

    def translate(self, dto: TranslateDTO, account_id: str):
        message = self.db.query(MessageEntity).filter_by(id=dto.message_id).first()
        content = message.content
        target_language = "zh_CN"
        messages = [
            {
                "role": "system",
                "content": "You are a translation engine that can only translate text and cannot interpret it, ensuring that the translation is clear, concise, and coherent.",
            },
            {
                "role": "user",
                "content": f"Please translate the following text into {target_language} Simplified: {content}",
            },
        ]
        result = self.__invoke_chat(messages)
        # 增加一条翻译记录，数据通过AccountTranslateEntity放到account_translate表中,
        # source_language通过message找到message_session的language
        message_session = (
            self.db.query(MessageSessionEntity).filter_by(id=message.session_id).first()
        )

        account_translate = AccountTranslateEntity(
            account_id=account_id,
            session_id=message.session_id,
            message_id=dto.message_id,
            target_language=target_language,
            source_language=message_session.language,
            source_text=content,
            target_text=result,
        )
        self.db.add(account_translate)
        self.db.commit()
        return result

    def message_speech_content(self, dto: TransformContentSpeechDTO, account_id: str):
        """如果file表中已经存在文件的保存，则直接返回，如果不存在，生成一份并保存"""
        # 根据convert_language与speech_role_name，speech_rate,speech_style来生成唯一标识,用于生成缓存的key
        key = (
            f"{dto.speech_role_name}_{dto.speech_rate}_{dto.speech_style}_{dto.content}"
        )
        file_module = "SPEECH_CONTENT_VOICE"
        # 对key进行md5加密
        key = hashlib.md5(key.encode("utf-8")).hexdigest()
        file_detail = (
            self.db.query(FileDetail)
            .filter_by(module=file_module, module_id=key, is_deleted=0)
            .first()
        )
        if file_detail:
            # 检查文件是否存在，只有文件存在情况下才进行返回
            if os.path.exists(f"{Config.TEMP_SAVE_FILE_PATH}/{file_detail.file_name}"):
                return {"file": file_detail.file_name}
            else:
                # 如果文件不存在，就删除数据库中的记录，重新生成
                file_detail.is_deleted = 1
                self.db.commit()

        # 调用speech组件，将speech_content转换成语音文件
        filename = f"{key}.wav"
        full_file_name = f"{Config.TEMP_SAVE_FILE_PATH}/{filename}"

        # 如何存在session_id 刚查出session后取出session的配置
        if dto.session_id:
            message_session = (
                self.db.query(MessageSessionEntity).filter_by(id=dto.session_id).first()
            )
            speech_role_name = message_session.speech_role_name
            speech_rate = message_session.speech_rate
            speech_style = message_session.speech_style
            language = message_session.language
        else:
            speech_role_name = dto.speech_role_name
            speech_rate = dto.speech_rate
            speech_style = dto.speech_style
            language = dto.language

        if speech_rate == "1.0" and not speech_style:
            speech(dto.content, full_file_name, voice_name=speech_role_name)
        else:
            speech_by_ssml(
                dto.content,
                full_file_name,
                voice_name=speech_role_name,
                speech_rate=speech_rate,
                feel=speech_style,
                targetLang=language,
            )
        file_detail = FileDetail(
            id=short_uuid(),
            file_path=filename,
            module=file_module,
            file_name=filename,
            module_id=key,
            file_ext="wav",
            created_by=account_id,
        )
        self.db.add(file_detail)
        self.db.commit()
        self.db.flush()
        return {"file": file_detail.file_name}

    def grammar_analysis(self, dto: GrammarDTO, account_id: str):
        message = self.db.query(MessageEntity).filter_by(id=dto.message_id).first()
        # 检查AccountGrammarEntity是否已经存在数据，如果存在就直接返回已经保存的数据
        account_grammar = (
            self.db.query(AccountGrammarEntity)
            .filter_by(
                message_id=dto.message_id, file_name=message.file_name, type="GRAMMAR"
            )
            .first()
        )
        if account_grammar:
            return json.loads(account_grammar.result)
        # 根据message获取session
        message_session = (
            self.db.query(MessageSessionEntity).filter_by(id=message.session_id).first()
        )
        content = message.content
        messages = [
            {
                "role": "system",
                "content": f"提供一段内容，只需要简洁快速的用中文返回这段内容中的语法错误，再根据提供的语言提供一句推荐示例，要求数据格式为json，语法是否错误放在属性isCorrect中，错误原因放在errorReason中，修正后的正确示例放在correctContent中，推荐示例放在better中，正确示例与推荐示例的语言要使用{message_session.language}",
            },
            {"role": "user", "content": f"内容: {content}"},
        ]
        result = json.loads(self.__invoke_chat(messages, temperature=0.2))
        result["original"] = content
        # result是json格式的字符串，把result 解析成json返回
        # 结果以字符串方式保存到数据库中
        account_grammar = AccountGrammarEntity(
            account_id=account_id,
            session_id=message.session_id,
            message_id=dto.message_id,
            file_name=message.file_name,
            type="GRAMMAR",
            result=json.dumps(result),
        )
        self.db.add(account_grammar)
        self.db.commit()
        return result

    def get_word(self, dto: WordDetailDTO, account_id: str):
        """通过AI获取单词的音标与翻译"""
        # 先查询数据库中是否有数据，如果有数据就直接返回
        word = self.db.query(SysCacheEntity).filter_by(key=f"word_{dto.word}").first()
        if word:
            return json.loads(word.value)
        # 如果没有数据，就调用AI接口获取数据
        messages = [
            {
                "role": "system",
                "content": f'提供一个单词，只需要简洁快速的用中文返回这个单词的音标与翻译，要求数据格式为json，音标放在属性phonetic中，音标的前后要加上"/"，翻译放在translation中， 这个单词是"{dto.word}"',
            }
        ]
        result = json.loads(self.__invoke_chat(messages))
        result["original"] = dto.word
        # result 转换成字符串进行保存
        sys_cache = SysCacheEntity(key=f"word_{dto.word}", value=json.dumps(result))
        self.db.add(sys_cache)
        self.db.commit()
        return result

    def word_practice(self, dto: WordPracticeDTO, account_id: str):
        """单词发音练习"""
        # 如果存在session_id，就根据session_id获取message_session的language
        if dto.session_id:
            message_session = (
                self.db.query(MessageSessionEntity).filter_by(id=dto.session_id).first()
            )
            language = message_session.language
        else:
            language = "en-US"
        return azure_voice.speech_pronunciation(
            dto.word, file_get_path(dto.file_name), language=language
        )

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
        if collect and collect.is_deleted == 0:
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
            collect.is_deleted = 1
            collect.update_time = datetime.now()
            self.db.commit()
        return

    def get_collects(self, type: str, page: int, page_size: int, account_id: str):
        """获取用户收藏的列表信息"""
        query = (
            self.db.query(AccountCollectEntity)
            .filter_by(account_id=account_id, type=type, is_deleted=0)
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

    def get_setting(self, account_id: str, key: str):
        """获取用户的设置"""
        settings = (
            self.db.query(AccountSettingsEntity)
            .filter_by(account_id=account_id, key=key)
            .first()
        )
        if not settings:
            return None
        return settings.value

    def get_settings(self, account_id: str):
        """获取AccountSettingsEntity中key 为 auto_playing_voice, playing_voice_speed, auto_text_shadow, auto_pronunciation的配置"""
        # 使用in操作获取key  为 auto_playing_voice, playing_voice_speed, auto_text_shadow, auto_pronunciation的配置
        settings = (
            self.db.query(AccountSettingsEntity)
            .filter(
                AccountSettingsEntity.account_id == account_id,
                AccountSettingsEntity.key.in_(
                    [
                        ACCOUNT_SETTINGS_AUTO_PLAYING_VOICE,
                        ACCOUNT_SETTINGS_PLAYING_VOICE_SPEED,
                        ACCOUNT_SETTINGS_AUTO_TEXT_SHADOW,
                        ACCOUNT_SETTINGS_AUTO_PRONUNCIATION,
                    ]
                ),
            )
            .all()
        )
        # 循环遍历settings，把key与value组装成AccountSettingsDTO返回
        result = {
            ACCOUNT_SETTINGS_AUTO_PLAYING_VOICE: True,
            ACCOUNT_SETTINGS_PLAYING_VOICE_SPEED: "1",
            ACCOUNT_SETTINGS_AUTO_TEXT_SHADOW: True,
            ACCOUNT_SETTINGS_AUTO_PRONUNCIATION: True,
        }
        for setting in settings:
            if setting.key == "playing_voice_speed":
                result[setting.key] = setting.value
            else:
                if setting.value == "1":
                    result[setting.key] = True
                else:
                    result[setting.key] = False
        return result

    def save_settings(self, dto: AccountSettingsDTO, account_id: str):
        """保存用户设置"""
        self.save_or_update_setting(
            account_id, ACCOUNT_SETTINGS_AUTO_PLAYING_VOICE, dto.auto_playing_voice
        )
        self.save_or_update_setting(
            account_id, ACCOUNT_SETTINGS_PLAYING_VOICE_SPEED, dto.playing_voice_speed
        )
        self.save_or_update_setting(
            account_id, ACCOUNT_SETTINGS_AUTO_TEXT_SHADOW, dto.auto_text_shadow
        )
        self.save_or_update_setting(
            account_id, ACCOUNT_SETTINGS_AUTO_PRONUNCIATION, dto.auto_pronunciation
        )

    def save_or_update_setting(self, account_id: str, key: str, value: str):
        settings = (
            self.db.query(AccountSettingsEntity)
            .filter_by(account_id=account_id, key=key)
            .first()
        )
        if not settings:
            settings = AccountSettingsEntity(
                account_id=account_id, key=key, value=value
            )
            self.db.add(settings)
        else:
            settings.value = value
        self.db.commit()
        return

    def prompt_sentence(self, dto: PromptDTO, account_id: str):
        """提示用户下一句话"""

        # 查询出session并获取对应的语言
        session = (
            self.db.query(MessageSessionEntity)
            .filter_by(id=dto.session_id, account_id=account_id)
            .first()
        )
        target_language = session.language

        target_language = session.language
        # 查询出session中最后5条消息
        messageEntities = (
            self.db.query(MessageEntity)
            .filter_by(session_id=dto.session_id)
            .order_by(MessageEntity.create_time.desc())
            .limit(5)
            .all()
        )
        system_content = "下面是一场对话\n"
        for message in reversed(messageEntities):
            if message.type == MessageType.SYSTEM.value:
                system_content = system_content + f"AI: {message.content}\n"
            else:
                system_content = system_content + f"用户: {message.content}\n"
        system_content = (
            system_content
            + "现在你需要做为一个用户来回答下一句话，只是答复不可以有提供帮助与提问问题的意思，要求给出3个不同答复，json数组格式，语言使用"
            + target_language
        )
        messages = [{"role": "system", "content": system_content}]

        result = self.__invoke_chat(messages, temperature=0.2)
        return json.loads(result)

    def add_feedback(self, dto: FeedbackDTO, account_id: str):
        add_feedback = FeedbackEntity(
            account_id=account_id, content=dto.content, contact=dto.contact
        )
        self.db.add(add_feedback)
        self.db.commit()
        self.db.refresh(add_feedback)

    def delete_all_session_messages(self, session_id: str, account_id: str):
        """把所有的消息都调整为is_deleted=1"""
        messages = (
            self.db.query(MessageEntity)
            .filter_by(session_id=session_id, account_id=account_id, is_deleted=0)
            .all()
        )
        for message in messages:
            message.is_deleted = 1
        self.db.commit()
        return True

    def delete_latest_session_messages(self, session_id: str, account_id: str):
        """查出最近的一条type为ACCOUNT的数据，并且把create_time之后的数据全部调整为is_deleted=1，删除成功后需要返回所有删除成功的message的id"""
        message = (
            self.db.query(MessageEntity)
            .filter_by(
                session_id=session_id,
                account_id=account_id,
                type=MessageType.ACCOUNT.value,
                is_deleted=0,
            )
            .order_by(MessageEntity.create_time.desc())
            .first()
        )
        if message:
            # 获取所有需要删除的数据
            messages = (
                self.db.query(MessageEntity)
                .filter_by(session_id=session_id, is_deleted=0)
                .filter(MessageEntity.create_time >= message.create_time)
                .all()
            )
            for message in messages:
                message.is_deleted = 1
            self.db.commit()
            return [message.id for message in messages]
        return []

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
            if collect.is_deleted == 1:
                collect.is_deleted = 0
                collect.update_time = datetime.now()

            self.db.commit()
            return

        # 查询出session
        if dto.message_id:
            message = (
                self.db.query(MessageEntity)
                .filter_by(id=dto.message_id, account_id=account_id)
                .first()
            )
            session = (
                self.db.query(MessageSessionEntity)
                .filter_by(id=message.session_id)
                .first()
            )
            session_id = session.id
            content = message.content
        else:
            session_id = None
            content = dto.content

        # 获得翻译
        translation = self.translate_text(
            TranslateTextDTO(text=content, target_language="zh-CN"), account_id
        )

        # 如果没有任何符号且只有单独一个单词，则type为WORD，否则为 SENTENCE
        if re.match(r"^[a-zA-Z]+$", content) and len(content.split(" ")) == 1:
            type = "WORD"
        else:
            type = "SENTENCE"

        account_collect = AccountCollectEntity(
            account_id=account_id,
            type=type,
            session_id=session_id,
            message_id=dto.message_id,
            content=content,
            translation=translation,
        )
        self.db.add(account_collect)

        self.db.commit()
        return

    def pronunciation(self, dto: PronunciationDTO, account_id: str):
        """发单评估"""
        # 先根据message_id查询出message
        message = self.db.query(MessageEntity).filter_by(id=dto.message_id).first()
        if not message:
            raise UserAccessDeniedException("message不存在")
        file_name = message.file_name
        if not file_name:
            raise UserAccessDeniedException("message中没有语音文件")

        # 检查AccountGrammarEntity是否已经存在数据，如果存在就直接返回已经保存的数据
        account_grammar = (
            self.db.query(AccountGrammarEntity)
            .filter_by(
                message_id=dto.message_id,
                file_name=message.file_name,
                type="PRONUNCIATION",
            )
            .first()
        )
        if account_grammar:
            return json.loads(account_grammar.result)

        file_full_path = file_get_path(file_name)
        # 检查文件是否存在
        if not os.path.exists(file_full_path):
            raise UserAccessDeniedException("语音文件不存在")
        # 进行评分
        try:
            logging.info("start")
            session = (
                self.db.query(MessageSessionEntity)
                .filter_by(id=message.session_id)
                .first()
            )
            pronunciation_result = azure_voice.speech_pronunciation(
                message.content, file_full_path, language=session.language
            )
            logging.info("end")

        except Exception as e:
            # 输出错误信息
            logging.exception(
                f"file_full_path:{file_full_path}\n content:{message.content}", e
            )
            raise UserAccessDeniedException("语音评估失败")
        # 结果以字符串方式保存到数据库中
        account_grammar = AccountGrammarEntity(
            account_id=account_id,
            session_id=message.session_id,
            message_id=dto.message_id,
            file_name=message.file_name,
            type="PRONUNCIATION",
            result=json.dumps(pronunciation_result),
        )
        self.db.add(account_grammar)
        self.db.commit()
        return pronunciation_result

    def __add_system_message(
        self, session_id, account_id: str, content: str
    ) -> MessageEntity:
        """添加系统消息"""
        add_message = MessageEntity(
            id=short_uuid(),
            account_id=account_id,
            sender=MESSAGE_SYSTEM,
            session_id=session_id,
            receiver=account_id,
            type=MessageType.SYSTEM.value,
            content=content,
            length=len(content),
        )
        self.db.add(add_message)
        self.db.commit()
        self.db.flush()
        self.__refresh_session_message_count(session_id)
        return add_message

    def __add_account_message(
        self, account_id: str, session_id: str, content: str, file_name: str = None
    ):
        """添加用户消息"""
        message = MessageEntity(
            id=short_uuid(),
            account_id=account_id,
            sender=account_id,
            session_id=session_id,
            receiver=MESSAGE_SYSTEM,
            type=MessageType.ACCOUNT.value,
            content=content,
            file_name=file_name,
            length=len(content),
        )
        self.db.add(message)
        self.db.commit()
        self.db.flush()
        self.__refresh_session_message_count(session_id)
        return message

    def __refresh_session_message_count(self, session_id: str):
        """刷新session的消息数量, 需要排除is_deleted为1的数据"""
        count = (
            self.db.query(MessageEntity)
            .filter(
                MessageEntity.session_id == session_id, MessageEntity.is_deleted == 0
            )
            .count()
        )
        self.db.query(MessageSessionEntity).filter(
            MessageSessionEntity.id == session_id
        ).update({"message_count": count})
        self.db.commit()
        self.db.flush()

    def __convert_session_model(self, session: MessageSessionEntity):
        # 通过SettingsRoleEntity来获取avatar
        settings_role = (
            self.db.query(SettingsRoleEntity)
            .filter_by(short_name=session.speech_role_name)
            .first()
        )
        if settings_role:
            teacher_avatar = settings_role.avatar
        else:
            teacher_avatar = ""
        return {
            "id": session.id,
            "gender": session.gender,
            "name": session.name,
            "scene": session.scene,
            "speech_role_name": session.speech_role_name,
            "language": session.language,
            "speech_rate": session.speech_rate,
            "speech_style": session.speech_style,
            "scene_content": session.scene_content,
            "message_count": session.message_count,
            "teacher_avatar": teacher_avatar,
            "create_time": date_to_str(session.create_time),
            "friendly_time": friendly_time(date_to_str(session.create_time)),
        }

    def __invoke_chat(self, messages: List[Dict], temperature=0.5):
        """调用chat gpt"""
        invoke_chat_json = chat_gpt_component.invoke_chat(
            ChatGPTInvokeDTO(
                messages=messages, max_tokens=300, temperature=temperature
            ),
            ApiKeyModel(
                organization=Config.CHAT_GPT_ORGANIZATION, api_key=Config.CHAT_GPT_KEY
            ),
        )
        invoke_result = invoke_chat_json["data"]

        return invoke_result
