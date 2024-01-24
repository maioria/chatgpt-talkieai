from sqlalchemy.orm import Session

from app.core.utils import *
from app.db.account_entities import *
from app.db.chat_entities import *
from app.db.sys_entities import *
from app.db.topic_entities import *
from app.models.account_models import *
from app.models.chat_models import *
from app.services.account_service import AccountService
from app.services.topic_service import TopicService

from app.ai.models import *
from app.ai import chat_ai
from app.core.azure_voice import *
from app.core.exceptions import *

MESSAGE_SYSTEM = "SYSTEM"

# 读取data下 language_demo_map.json 生成对应字典
language_demo_map = {}
with open("data/language_demo_map.json", "r") as f:
    language_demo_map = json.load(f)


class ChatService:
    """聊天核心类，会调用account_service与topic_service, 反向不可以引用"""

    def __init__(self, db: Session):
        self.db = db
        self.account_service = AccountService(db)
        self.topic_service = TopicService(db)

    def get_settings_languages_example(self, language: str, account_id: str):
        """获取语言下的示例"""
        # 获取语言下的示例
        # 语言没有国家  所以去掉后面的国家后缀
        language = language.split("-")[0]
        return language_demo_map[language]

    def get_default_session(self, account_id: str):
        """获取用户的默认会话, 如果没有默认会话，就创建一个"""
        session = (
            self.db.query(MessageSessionEntity)
            .filter_by(
                account_id=account_id,
                is_default=1,
            )
            .order_by(MessageSessionEntity.create_time.desc())
            .first()
        )
        if not session:
            # 为用户创建一个默认的session
            return self.create_session(
                account_id,
            )
        return self.__convert_session_model(session)

    def get_session(self, session_id: str, account_id: str):
        """获取会话详情"""
        session = self.__get_and_check_session(session_id, account_id)
        result = self.__convert_session_model(session)

        # 获取会话下的消息
        result["messages"] = self.get_session_messages(session_id, account_id, 1, 100)
        return result

    def get_session_greeting(self, session_id: str, account_id: str):
        """需要会话没有任何消息时，需要返回的问候语"""

        # 检查session是否存在
        session = self.__get_and_check_session(session_id, account_id)

        # 检查会话下是否已经有了消息
        self.__check_has_messages(session_id, account_id)

        # 区分自由聊天与话题聊天
        if session.type == "CHAT":
            language = self.account_service.get_account_target_language(account_id)
            result = chat_ai.invoke_greet(GreetParams(language=language))
        elif session.type == "TOPIC":
            topic_greet_params = self.topic_service.get_topic_greet_params(session.id)
            result = chat_ai.topic_invoke_greet(topic_greet_params)

        sequence = self.__get_message_sequence() 

        add_message = self.__add_system_message(session_id, account_id, result, "", sequence + 1)
        self.db.add(add_message)
        self.db.commit()
        self.db.flush()
        self.__refresh_session_message_count(session_id)
        return self.initMessageResult(add_message)

    def send_session_message(self, session_id: str, dto: ChatDTO, account_id: str):
        """发送消息"""
        # 如果有file_name却没有message，需要解析出message
        if not dto.file_name and not dto.message:
            raise Exception("Message or file_name is required")
        
        session = self.__get_and_check_session(session_id, account_id)

        account_settins = (
            self.db.query(AccountSettingsEntity)
            .filter_by(account_id=account_id)
            .first()
        )
        target_language = account_settins.target_language
        if dto.message:
            send_message_content = dto.message
        else:
            send_message_content = speech_translate_text(
                voice_file_get_path(dto.file_name), target_language
            )

        # 获取前面的sequence
        sequence = self.__get_message_sequence()

        add_account_message = self.__add_account_message(
            account_id, session_id, send_message_content, sequence + 1, dto.file_name
        )

        send_message_id = add_account_message.id
        message_history = (
            self.db.query(MessageEntity)
            .filter(MessageEntity.session_id == session_id)
            .order_by(MessageEntity.create_time.desc())
            .slice(0, 5)
            .all()
        )
        messages = []
        for message in reversed(message_history):
            if message.type == MessageType.SYSTEM.value:
                messages.append({"role": "assistant", "content": message.content})
            else:
                messages.append({"role": "user", "content": message.content})
        
        # 补充上用户新加的这个
        messages.append({"role": "user", "content": send_message_content})

        completed = False
        if session.type == 'CHAT':
            speech_role_name = account_settins.speech_role_name
            styles = []
            if speech_role_name:
                voice_role_config = get_azure_voice_role_by_short_name(speech_role_name)
                styles = voice_role_config["style_list"]
            message_params = MessageParams(
                language=target_language, name=Config.AI_NAME, messages=messages, styles=styles
            )
            invoke_result = chat_ai.invoke_message(message_params)
        elif session.type == 'TOPIC':
            topic_message_params = self.topic_service.get_topic_message_params(session.id)
            topic_message_params.messages = messages
            invoke_result = chat_ai.topic_invoke_message(topic_message_params)
            completed = invoke_result.completed

        add_system_message = self.__add_system_message(
            session_id,
            account_id,
            invoke_result.message,
            invoke_result.message_style,
            sequence + 2,
        )
        self.db.add(add_account_message)
        self.db.add(add_system_message)
        self.db.commit()
        self.db.flush()
        self.__refresh_session_message_count(session_id)
        return {
            "data": invoke_result.message,
            "id": add_system_message.id,
            "session_id": session_id,
            "send_message_id": send_message_id,
            "send_message_content": send_message_content,
            "create_time": date_to_str(add_system_message.create_time),
            "completed": completed,
        }

    def message_practice(
        self, message_id: str, dto: MessagePracticeDTO, account_id: str
    ):
        """用户发送过的消息进行练习"""
        message = self.db.query(MessageEntity).filter_by(id=message_id).first()
        if not message:
            raise Exception("Message not found")
        target_language = self.account_service.get_account_target_language(account_id)
        return word_speech_pronunciation(
            message.content, voice_file_get_path(dto.file_name), target_language
        )

    def get_word(self, dto: WordDetailDTO, account_id: str):
        """通过AI获取单词的音标与翻译"""
        # 先查询数据库中是否有数据，如果有数据就直接返回
        word = self.db.query(SysCacheEntity).filter_by(key=f"word_{dto.word}").first()
        if word:
            return json.loads(word.value)
        invoke_result = chat_ai.invoke_word_detail(WordDetailParams(word=dto.word))
        result = invoke_result.__dict__
        result["original"] = dto.word
        # result 转换成字符串进行保存
        sys_cache = SysCacheEntity(key=f"word_{dto.word}", value=json.dumps(result))
        self.db.add(sys_cache)
        self.db.commit()
        return result

    def grammar_analysis(self, dto: GrammarDTO, account_id: str):
        message = self.db.query(MessageEntity).filter_by(id=dto.message_id).first()
        # 检查AccountGrammarEntity是否已经存在数据，如果存在就直接返回已经保存的数据
        message_grammar = (
            self.db.query(MessageGrammarEntity)
            .filter_by(
                message_id=dto.message_id, file_name=message.file_name, type="GRAMMAR"
            )
            .first()
        )
        if message_grammar:
            return json.loads(message_grammar.result)

        content = message.content
        target_language = self.account_service.get_account_target_language(account_id)
        result = chat_ai.invoke_grammar_analysis(
            GrammarAnalysisParams(language=target_language, content=content)
        ).__dict__
        result["original"] = content
        # result是json格式的字符串，把result 解析成json返回
        # 结果以字符串方式保存到数据库中
        message_grammar = MessageGrammarEntity(
            account_id=account_id,
            session_id=message.session_id,
            message_id=dto.message_id,
            file_name=message.file_name,
            type="GRAMMAR",
            result=json.dumps(result),
        )
        self.db.add(message_grammar)
        self.db.commit()
        return result

    def word_practice(self, dto: WordPracticeDTO, account_id: str):
        """单词发音练习"""
        target_language = self.account_service.get_account_target_language(account_id)
        return word_speech_pronunciation(
            dto.word, voice_file_get_path(dto.file_name), language=target_language
        )

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
        grammar = (
            self.db.query(MessageGrammarEntity)
            .filter_by(
                message_id=dto.message_id,
                file_name=message.file_name,
                type="PRONUNCIATION",
            )
            .first()
        )
        if grammar:
            return json.loads(grammar.result)

        file_full_path = voice_file_get_path(file_name)
        # 检查文件是否存在
        if not os.path.exists(file_full_path):
            raise UserAccessDeniedException("语音文件不存在")
        target_language = self.account_service.get_account_target_language(account_id)
        # 进行评分
        try:
            session = (
                self.db.query(MessageSessionEntity)
                .filter_by(id=message.session_id)
                .first()
            )
            pronunciation_result = word_speech_pronunciation(
                message.content, file_full_path, language=target_language
            )
            logging.info("end")
        except Exception as e:
            # 输出错误信息
            logging.exception(
                f"file_full_path:{file_full_path}\n content:{message.content}", e
            )
            raise UserAccessDeniedException("语音评估失败")
        # 结果以字符串方式保存到数据库中
        message_grammar = MessageGrammarEntity(
            account_id=account_id,
            session_id=message.session_id,
            message_id=dto.message_id,
            file_name=message.file_name,
            type="PRONUNCIATION",
            result=json.dumps(pronunciation_result),
        )
        self.db.add(message_grammar)
        self.db.commit()
        return pronunciation_result

    def message_speech_content(self, dto: TransformContentSpeechDTO, account_id: str):
        """如果file表中已经存在文件的保存，则直接返回，如果不存在，生成一份并保存"""
        # 根据convert_language与speech_role_name，speech_rate,speech_style来生成唯一标识,用于生成缓存的key
        # 获取用户语言
        account_settings = (
            self.db.query(AccountSettingsEntity)
            .filter_by(account_id=account_id)
            .first()
        )
        target_language = account_settings.target_language
        set_speech_role_name = None
        set_speech_role_style = ""
        if dto.speech_role_name:
            set_speech_role_name = dto.speech_role_name
            if dto.speech_role_style:
                set_speech_role_style = dto.speech_role_style
        elif account_settings.speech_role_name:
            set_speech_role_name = account_settings.speech_role_name

        set_speech_rate = "1.0"
        if dto.speech_rate:
            set_speech_rate = dto.speech_rate
        elif account_settings.speech_role_speed:
            set_speech_rate = account_settings.speech_role_speed

        content_md5 = hashlib.md5(dto.content.encode("utf-8")).hexdigest()
        key = f"content_{set_speech_role_name}_{set_speech_role_style}_{set_speech_rate}_{content_md5}"
        file_module = "SPEECH_CONTENT_VOICE"
        # 对key进行md5加密
        file_detail = (
            self.db.query(FileDetail)
            .filter_by(module=file_module, module_id=key, deleted=0)
            .first()
        )
        if file_detail:
            # 检查文件是否存在，只有文件存在情况下才进行返回
            if os.path.exists(voice_file_get_path(file_detail.file_name)):
                return {"file": file_detail.file_name}
            else:
                # 如果文件不存在，就删除数据库中的记录，重新生成
                file_detail.deleted = 1
                self.db.commit()

        # 调用speech组件，将speech_content转换成语音文件
        filename = f"{key}.wav"
        full_file_name = voice_file_get_path(filename)

        if set_speech_rate != "1.0" or set_speech_role_style:
            speech_by_ssml(
                dto.content,
                full_file_name,
                voice_name=set_speech_role_name,
                speech_rate=set_speech_rate,
                feel=set_speech_role_style,
                targetLang=target_language,
            )
        else:
            speech_default(
                dto.content, full_file_name, target_language, set_speech_role_name
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

    def message_speech(self, message_id: str, account_id: str):
        """文字转语音"""
        # 如果没有，就生成一个
        message = self.db.query(MessageEntity).filter_by(id=message_id).first()

        # 获取用户的语音配置
        account_settings = (
            self.db.query(AccountSettingsEntity)
            .filter_by(account_id=account_id)
            .first()
        )
        target_language = account_settings.target_language
        voice_name = account_settings.speech_role_name
        speech_speed = account_settings.playing_voice_speed
        filename = f"message_{message.id}_{voice_name}_{speech_speed}.wav"
        full_file_name = voice_file_get_path(filename)
        voice_role_style = ""
        if message.style:
            voice_role_style = message.style
        speech_by_ssml(
            message.content,
            full_file_name,
            voice_name=voice_name,
            speech_rate=speech_speed,
            feel=voice_role_style,
            targetLang=target_language,
        )

        file_detail = FileDetail(
            id=short_uuid(),
            file_path=filename,
            module="SPEECH_VOICE",
            file_name=filename,
            module_id=message_id,
            file_ext="wav",
            created_by=account_id,
        )
        self.db.add(file_detail)
        message.file_name = filename
        self.db.commit()
        return {"file": file_detail.file_name}

    def create_session(self, account_id: str):
        """为用户创建新的session，并且设置成默认的session"""
        session = MessageSessionEntity(
            id=f"session_{short_uuid()}", account_id=account_id, is_default=1
        )
        self.db.add(session)
        self.db.commit()
        return self.__convert_session_model(session)

    def get_session_messages(
        self, session_id: str, account_id: str, page: int, page_size: int
    ):
        query = (
            self.db.query(MessageEntity)
            .filter_by(session_id=session_id, account_id=account_id, deleted=0)
            .filter(
                MessageEntity.type.in_(
                    [MessageType.ACCOUNT.value, MessageType.SYSTEM.value]
                )
            )
        )
        messages = (
            query.order_by(MessageEntity.sequence.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        # 获取总数
        total = query.count()
        result = []
        for message in reversed(messages):
            result.append(self.initMessageResult(message))

        # 如果是我的消息，则检查是否进行过语音分析，如果进行过就加载分析结果
        self.initOwnerMessagePronunciation(result)
        return {"total": total, "list": result}

    def prompt_sentence(self, dto: PromptDTO, account_id: str):
        """提示用户下一句话"""
        # 查询出session中最后5条消息
        messageEntities = (
            self.db.query(MessageEntity)
            .filter_by(session_id=dto.session_id)
            .order_by(MessageEntity.create_time.desc())
            .limit(5)
            .all()
        )
        messages = []
        for message in messageEntities:
            messages.append(self.initMessageResult(message))

        target_language = self.account_service.get_account_target_language(account_id)
        return chat_ai.invoke_prompt_sentence(
            PromptSentenceParams(language=target_language, messages=messages)
        )

    def delete_all_session_messages(self, session_id: str, account_id: str):
        """把所有的消息都调整为deleted=1"""
        messages = (
            self.db.query(MessageEntity)
            .filter_by(session_id=session_id, account_id=account_id, deleted=0)
            .all()
        )
        for message in messages:
            message.deleted = 1
        self.db.commit()
        return True

    def transform_text(self, session_id: str, dto: VoiceTranslateDTO, account_id: str):
        """语音解析成文字"""

        result = speech_translate_text(
            voice_file_get_path(dto.file_name),
            self.account_service.get_account_target_language(account_id),
        )
        return result

    def delete_latest_session_messages(self, session_id: str, account_id: str):
        """查出最近的一条type为ACCOUNT的数据，并且把create_time之后的数据全部调整为deleted=1，删除成功后需要返回所有删除成功的message的id"""
        message = (
            self.db.query(MessageEntity)
            .filter_by(
                session_id=session_id,
                account_id=account_id,
                type=MessageType.ACCOUNT.value,
                deleted=0,
            )
            .order_by(MessageEntity.create_time.desc())
            .first()
        )
        if message:
            # 获取所有需要删除的数据
            messages = (
                self.db.query(MessageEntity)
                .filter_by(session_id=session_id, deleted=0)
                .filter(MessageEntity.create_time >= message.create_time)
                .all()
            )
            for message in messages:
                message.deleted = 1
            self.db.commit()
            return [message.id for message in messages]
        return []

    def initOwnerMessagePronunciation(self, result):
        # 过滤出所有role为USER的id列表，然后根据id列表获取所有的message_pronunciation，再组装到item中，不存在则组装None
        user_message_ids = [item["id"] for item in result if item["role"] == "USER"]
        message_pronunciations = (
            self.db.query(MessageGrammarEntity)
            .filter(
                MessageGrammarEntity.message_id.in_(user_message_ids),
                MessageGrammarEntity.type == "PRONUNCIATION",
            )
            .all()
        )
        for item in result:
            if item["role"] == "USER":
                item["pronunciation"] = None
                for message_pronunciation in message_pronunciations:
                    if message_pronunciation.message_id == item["id"]:
                        item["pronunciation"] = json.loads(message_pronunciation.result)
                        break

    def translate_source_language(self, dto: TranslateTextDTO, account_id: str):
        """翻译成源语言"""
        source_language = self.account_service.get_account_source_language(account_id)
        result = self.translate_language(dto.text, source_language)
        return result

    def translate_setting_language(self, dto: TranslateTextDTO, account_id: str):
        """翻译成目标语言，也就是用户学习的语言"""
        # 获取用户配置language
        account_settings = (
            self.db.query(AccountSettingsEntity)
            .filter_by(account_id=account_id)
            .first()
        )
        result = self.translate_language(dto.text, account_settings.target_language)
        return result

    def translate_language(self, content: str, language: str):
        """翻译成参数中配置的语言"""
        result = chat_ai.invoke_translate(
            TranslateParams(target_language=language, content=content)
        )
        return result

    def translate_message(self, message_id: str, account_id: str):
        # 检查是否已经生成了对应翻译，生成的话直接返回
        message_translate = (
            self.db.query(MessageTranslateEntity)
            .filter_by(message_id=message_id)
            .first()
        )
        if message_translate:
            return message_translate.target_text

        message = self.db.query(MessageEntity).filter_by(id=message_id).first()
        content = message.content
        source_language = self.account_service.get_account_source_language(account_id)
        target_language = self.account_service.get_account_target_language(account_id)
        result = self.translate_source_language(
            TranslateTextDTO(text=content), account_id
        )

        account_translate = MessageTranslateEntity(
            account_id=account_id,
            session_id=message.session_id,
            message_id=message_id,
            target_language=target_language,
            source_language=source_language,
            source_text=content,
            target_text=result,
        )
        self.db.add(account_translate)
        self.db.commit()
        return result

    def initMessageResult(self, message: MessageEntity):
        return {
            "role": "ASSISTANT" if message.type == MessageType.SYSTEM.value else "USER",
            "content": message.content,
            "file_name": message.file_name,
            "id": message.id,
            "create_time": date_to_str(message.create_time),
            "session_id": message.session_id,
        }

    def __convert_session_model(self, session: MessageSessionEntity):
        return {
            "id": session.id,
            "type": session.type,
            "message_count": session.message_count,
            "create_time": date_to_str(session.create_time),
            "friendly_time": friendly_time(date_to_str(session.create_time)),
        }

    def __add_account_message(
        self, account_id: str, session_id: str, content: str, sequence: int, file_name: str = None
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
            sequence=sequence,
        )
        return message

    def __add_system_message(
        self, session_id, account_id: str, content: str, style: str, sequence: int
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
            style=style,
            length=len(content),
            sequence=sequence,
        )
        return add_message

    def __refresh_session_message_count(self, session_id: str):
        """刷新session的消息数量, 需要排除deleted为1的数据"""
        count = (
            self.db.query(MessageEntity)
            .filter(MessageEntity.session_id == session_id, MessageEntity.deleted == 0)
            .count()
        )
        self.db.query(MessageSessionEntity).filter(
            MessageSessionEntity.id == session_id
        ).update({"message_count": count})
        self.db.commit()
        self.db.flush()

    def __get_and_check_session(
        self, session_id: str, account_id: str
    ) -> MessageSessionEntity:
        """检查会话是否存在"""
        session = (
            self.db.query(MessageSessionEntity)
            .filter_by(id=session_id, account_id=account_id)
            .first()
        )
        if not session:
            raise Exception("Session not found")
        return session

    def __check_has_messages(self, session_id: str, account_id: str):
        """检查会话下是否已经有了消息"""
        messages = (
            self.db.query(MessageEntity)
            .filter_by(session_id=session_id, account_id=account_id, deleted=0)
            .order_by(MessageEntity.create_time.desc())
            .slice(0, 1)
            .all()
        )
        if len(messages) == 1:
            raise Exception("Session has messages")
        
    def __get_message_sequence(self):
        """获取当前最大的sequence"""
        sequence = (
            self.db.query(MessageEntity)
            .filter_by(deleted=0)
            .order_by(MessageEntity.sequence.desc())
            .first()
        )
        if sequence:
            return sequence.sequence
        return 0    
