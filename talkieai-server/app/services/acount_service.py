import json
import os
from datetime import datetime
from string import Template
from typing import List, Dict

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.chat_gpt import ApiKeyModel, ChatGPTInvokeDTO, ChatGptLocalComponent
from app.core.utils import short_uuid, save_file, date_to_str, friendly_time, day_to_str
from app.core import auth, speech_component
from app.core.exceptions import UserAccessDeniedException, ParameterIncorrectException
from app.db.entities import VisitorEntity, MessageSessionEntity, MessageEntity, FileDetail, AccountTranslateEntity, \
    AccountPromptEntity, SysCacheEntity
from app.config import Config
from app.models.chat_models import ChatDTO, MessageType, TransformSpeechDTO, TranslateDTO, GrammarDTO, PromptDTO, \
    SessionCreateDTO, DemoTranslateDTO, SpeechDemoDTO, AccountUsageType

MESSAGE_SYSTEM = 'SYSTEM'
chat_gpt_component = ChatGptLocalComponent()
CREATE_SESSION_DEMO_CONTENT = '你好，欢迎使用Talkie，希望您能有一个好的学习体验。'

"""加载json文件，试听的时候取出对应内容转换成语音"""
# 加载项目data文件夹下的language_demo_map.json文件，通过json转换成数据字典，获取当前项目下的执行路径
current_path = os.path.dirname(os.path.abspath(__file__))
# 将路径下前俩个目录截取掉
current_path = os.path.dirname(current_path)
# 将路径下的data文件夹拼接到路径中
current_path = os.path.join(current_path, 'data')
with open(current_path + '/language_demo_map.json', 'r', encoding='utf-8') as f:
    language_demo_map = json.load(f)


class AccountService:
    def __init__(self, db: Session):
        self.db = db

    def visitor_login(self, fingerprint: str, client_host: str, user_agent: str = None):
        """先检查此ip下是否有用户，如果有，直接返回ip下的用户，如果没有，就生成新的访客"""
        visitor = self.db.query(VisitorEntity).filter_by(fingerprint=fingerprint).first()
        if not visitor:
            visitor = VisitorEntity(id=f'visitor_{short_uuid()}', fingerprint=fingerprint,
                                    client_host=client_host,
                                    user_agent=user_agent)
            self.db.add(visitor)
            self.db.commit()
        return auth.init_token(visitor.id, visitor.id)

    def get_user_info(self, account_id: str):
        """游客登录并没有任何信息"""

        # 检查visitor表中是否有此用户
        visitor = self.db.query(VisitorEntity).filter_by(id=account_id).first()
        if not visitor:
            raise UserAccessDeniedException()

        user_info = {'id': account_id}
        return user_info

    def get_user_info_usage(self, account_id: str):
        """message表中type为SYSTEM并且file_name不为空的记录为语音转换,
        message表中type为ACCOUNT并且file_name不为空的记录为发送语音,
        通过message表中取出当天系统返回的次数(type为SYSTEM)，发送语音次数，语音转换次数，把数据装配好返回"""
        system_count = self.get_user_current_day_system_message_count(account_id)

        transform_count = self.get_user_current_day_transform_count(account_id)

        speech_count = self.get_user_current_day_speech_count(account_id)

        prompt_count = self.get_user_current_day_prompt_count(account_id)

        result = {'system_count': system_count,
                  'transform_count': transform_count,
                  'speech_count': speech_count,
                  'prompt_count': prompt_count,
                  'day_system_count': Config.MAX_DAY_SYSTEM_MESSAGE_COUNT,
                  'day_transform_count': Config.MAX_DAY_TEXT_TO_VOICE_COUNT,
                  'day_speech_count': Config.MAX_DAY_SPEECH_COUNT,
                  'day_prompt_count': Config.MAX_DAY_PROMPT_COUNT}
        return result

    def get_user_current_day_system_message_count(self, account_id: str):
        """获取用户当天系统消息次数"""
        today = day_to_str(datetime.now())
        return self.db.query(MessageEntity).filter_by(account_id=account_id, type=MessageType.SYSTEM.value).filter(
            MessageEntity.create_time >= today).count()

    def get_user_current_day_prompt_count(self, account_id: str):
        """获取用户当天提示消息次数"""
        today = day_to_str(datetime.now())
        result = self.db.query(AccountPromptEntity).filter_by(account_id=account_id).filter(
            AccountPromptEntity.create_time >= today).count()
        return result

    def get_user_current_day_speech_count(self, account_id):
        """获取用户当天发送语音次数"""
        today = day_to_str(datetime.now())
        return self.db.query(MessageEntity) \
            .filter_by(account_id=account_id, type=MessageType.ACCOUNT.value, is_deleted=0) \
            .filter(MessageEntity.create_time >= today) \
            .filter(MessageEntity.file_name != None).count()

    def get_user_current_day_transform_count(self, account_id: str):
        """获取用户当天语音转换次数"""
        today = day_to_str(datetime.now())
        return self.db.query(MessageEntity) \
            .filter_by(account_id=account_id, type=MessageType.SYSTEM.value,
                       is_deleted=0).filter(MessageEntity.create_time >= today).filter(
            MessageEntity.file_name != None).count()

    def language_demo_content(self, dto: DemoTranslateDTO, account_id: str):
        """演示翻译， 增加缓存，如果缓存中有，就直接返回，如果没有，就调用翻译接口，然后返回，缓存从缓存表中获取(SysCacheEntity)"""
        # 如果是中文标识(小写后为zh开头)， 就直接返回默认
        if dto.language.lower().startswith('zh'):
            return CREATE_SESSION_DEMO_CONTENT
        # 如果language包含 '-' 则只需要取前面的部分
        convert_language = ''
        if '-' in dto.language:
            convert_language = dto.language.split('-')[0]
        key = 'demo_translate_' + convert_language

        cache = self.db.query(SysCacheEntity).filter_by(key=key).first()
        if cache:
            return cache.value
        else:
            result = self.__translate_content(CREATE_SESSION_DEMO_CONTENT, dto.language)
            self.db.add(SysCacheEntity(key=key, value=result))
            self.db.commit()
            return result

    def create_session(self, dto: SessionCreateDTO, account_id):
        """创建会话"""
        # 需要先对用户进行检查，一个用户最多创建10个会话
        self.check_user_session_limit(account_id)

        session = MessageSessionEntity(id=f'session_{short_uuid()}',
                                       account_id=account_id,
                                       gender=dto.gender,
                                       teacher_avatar=dto.teacher_avatar,
                                       name=dto.name,
                                       language=dto.language,
                                       scene=dto.scene.value,
                                       scene_content=dto.scene_content,
                                       speech_role_name=dto.speech_role_name,
                                       speech_rate=dto.speech_rate,
                                       speech_style=dto.speech_style)
        self.db.add(session)
        self.db.commit()
        return session.id

    def delete_session(self, session_id: str, account_id: str):
        """检查session是否是这个用户的，如果是这个用户的，调整is_deleted=1"""
        session = self.db.query(MessageSessionEntity).filter_by(id=session_id, account_id=account_id,
                                                                is_deleted=0).first()
        if session:
            session.is_deleted = 1
            self.db.commit()
            return True
        return False

    def get_session_count(self, account_id: str):
        return self.db.query(MessageSessionEntity).filter_by(account_id=account_id, is_deleted=0).count()

    def get_session_list(self, account_id: str, page: int, page_size: int):
        """分页获取用户的会话数据"""
        query = self.db.query(MessageSessionEntity).filter_by(account_id=account_id, is_deleted=0)
        sessions = query.order_by(
            MessageSessionEntity.create_time.desc()).offset((page - 1) * page_size).limit(page_size).all()
        # 获取总数
        total = query.count()
        result = []
        for session in sessions:
            result.append(
                self.__convert_session_model(session))
        return {'total': total, 'list': result}

    def get_session(self, session_id, account_id: str):
        """获取message_session详情"""
        session = self.db.query(MessageSessionEntity).filter_by(account_id=account_id, id=session_id,
                                                                is_deleted=0).first()
        if session is None:
            raise Exception('会话不存在')
        return self.__convert_session_model(session)

    def get_session_messages(self, session_id: str, account_id: str, page: int, page_size: int):
        query = self.db.query(MessageEntity).filter_by(account_id=account_id, session_id=session_id, is_deleted=0)
        messages = query.order_by(
            MessageEntity.create_time.desc()).offset((page - 1) * page_size).limit(page_size).all()
        # 获取总数
        total = query.count()
        result = []
        for message in reversed(messages):
            result.append(
                {'role': 'ASSISTANT' if message.type == MessageType.SYSTEM.value else 'USER',
                 'content': message.content, 'file_name': message.file_name, 'id': message.id,
                 'create_time': date_to_str(message.create_time)})
        return {'total': total, 'list': result}

    def delete_all_session_messages(self, session_id: str, account_id: str):
        """把所有的消息都调整为is_deleted=1"""
        messages = self.db.query(MessageEntity).filter_by(session_id=session_id, account_id=account_id,
                                                          is_deleted=0).all()
        for message in messages:
            message.is_deleted = 1
        self.db.commit()
        return True

    def delete_latest_session_messages(self, session_id: str, account_id: str):
        """查出最近的一条type为ACCOUNT的数据，并且把create_time之后的数据全部调整为is_deleted=1，删除成功后需要返回所有删除成功的message的id"""
        message = self.db.query(MessageEntity).filter_by(session_id=session_id, account_id=account_id,
                                                         type=MessageType.ACCOUNT.value,
                                                         is_deleted=0).order_by(
            MessageEntity.create_time.desc()).first()
        if message:
            # 获取所有需要删除的数据
            messages = self.db.query(MessageEntity).filter_by(session_id=session_id, is_deleted=0).filter(
                MessageEntity.create_time >= message.create_time).all()
            for message in messages:
                message.is_deleted = 1
            self.db.commit()
            return [message.id for message in messages]
        return []

    def voice_upload(self, session_id: str, file: UploadFile,
                     account_id: str):
        """获取用户当天使用的语音数量，如果超过了配置数量则抛出错误"""
        self.check_user_current_day_limit(account_id, AccountUsageType.SPEECH)

        # 保存文件
        file_name = f'{short_uuid("FILE")}.wav'
        save_file(file, f'{Config.TEMP_SAVE_FILE_PATH}', file_name)
        # 查询到session并且获取到session的language
        session = self.db.query(MessageSessionEntity).filter_by(id=session_id, account_id=account_id).first()
        result = speech_component.translate_text(f'{Config.TEMP_SAVE_FILE_PATH}/{file_name}', session.language)
        return {'result': result, 'file': file_name}

    def send_message(self, dto: ChatDTO, account_id: str):
        """发送消息,获取用户当天收到的所有系统消息数量，如果超过了配置数量则抛出错误"""
        self.check_user_current_day_limit(account_id, AccountUsageType.CHAT)

        session_id = dto.session_id
        # 查询到session
        session = self.db.query(MessageSessionEntity).filter_by(id=session_id, account_id=account_id).first()
        send_message = self.__add_account_message(account_id, session_id, dto.message, dto.file_name)
        send_message_id = send_message.id

        # 生成system的配置
        base_template_str = 'I want you to act as an $language speaking partner and improver, your name is $name. No matter what language I speak to you, you need to reply me in $language. I hope you keep your responses clean and limit your responses to 80 characters. I hope you will ask me a question from time to time in your reply. Now let\'s start practicing. Remember, I want you reply me in $language and your name is $name and do not respond with any other information about yourself.'
        if session.speech_style:
            base_template_str = base_template_str + ' I want you to keep your tone ' + session.speech_style + '.'
        system_content_template = Template(base_template_str)
        params = {'language': session.language, 'name': 'Talkie'}
        system_content = system_content_template.substitute(params)

        # 组装messages
        messages = [{"role": "system", "content": system_content}]
        message_history = self.db.query(MessageEntity).filter(
            MessageEntity.session_id == session_id).order_by(
            MessageEntity.create_time.desc()).slice(0, 6).all()
        for message in reversed(message_history):
            if message.type == MessageType.SYSTEM.value:
                messages.append({'role': 'assistant', 'content': message.content})
            else:
                messages.append({'role': 'user', 'content': message.content})

        # 调用chat获取结果
        invoke_result = self.__invoke_chat(messages)
        add_message = self.__add_system_message(session_id, account_id, invoke_result)
        return {'data': invoke_result,
                'id': add_message.id,
                'session_id': session_id,
                'send_message_id': send_message_id,
                'create_time': date_to_str(add_message.create_time)
                }

    def translate(self, dto: TranslateDTO, account_id: str):
        """对message的内容进行翻译"""
        message = self.db.query(MessageEntity).filter_by(id=dto.message_id, account_id=account_id).first()
        content = message.content
        target_language = 'zh_CN'

        # 执行翻译
        result = self.__translate_content(content, target_language)

        # 增加一条翻译记录，数据通过AccountTranslateEntity放到account_translate表中,
        message_session = self.db.query(MessageSessionEntity).filter_by(id=message.session_id).first()

        account_translate = AccountTranslateEntity(account_id=account_id,
                                                   session_id=message.session_id,
                                                   message_id=dto.message_id,
                                                   target_language=target_language,
                                                   source_language=message_session.language,
                                                   source_text=content,
                                                   target_text=result)
        self.db.add(account_translate)
        self.db.commit()
        return result

    def grammar_analysis(self, dto: GrammarDTO, account_id: str):
        """分析用户的语法问题"""
        message = self.db.query(MessageEntity).filter_by(id=dto.message_id, account_id=account_id).first()
        content = message.content
        messages = [
            {"role": "system",
             "content": '提供一段内容，只需要简洁快速的用中文返回这段内容中的语法错误'},
            {"role": "user",
             "content": f'内容: {content}'}
        ]
        return self.__invoke_chat(messages)

    def prompt_sentence(self, dto: PromptDTO, account_id: str):
        """系统生成提示语句"""

        # 获取用户当天的prompt次数
        self.check_user_current_day_limit(account_id, AccountUsageType.PROMPT)

        # 查询出session并获取对应的语言
        session = self.db.query(MessageSessionEntity).filter_by(id=dto.session_id, account_id=account_id).first()
        target_language = session.language

        system_content_template = Template(
            'You need to help people generate a positive response based on the previous sentence with $language, keeping it concise and without any additional information and do not ask any questions.')
        params = {'language': target_language, 'name': 'Talkie'}
        system_content = system_content_template.substitute(params)

        # 查询出session中最后1条消息
        messageEntities = self.db.query(MessageEntity).filter_by(session_id=dto.session_id).order_by(
            MessageEntity.create_time.desc()).limit(1).all()
        messages = [{"role": "system", "content": system_content},
                    {"role": "user", "content": messageEntities[0].content}]
        result = self.__invoke_chat(messages)
        account_prompt = AccountPromptEntity(account_id=account_id,
                                             session_id=dto.session_id,
                                             message_id=dto.message_id,
                                             prompt_type='PROMPT',
                                             source_language='zh_CN',
                                             target_language=target_language,
                                             source_text='',
                                             target_text=result)
        self.db.add(account_prompt)
        self.db.commit()
        return result

    def message_speech_demo(self, dto: SpeechDemoDTO, account_id: str):
        """如果file表中已经存在文件的保存，则直接返回，如果不存在，生成一份并保存"""
        convert_language = dto.language.split('-')[0]
        # 根据convert_language与speech_role_name，speech_rate,speech_style来生成唯一标识,用于生成缓存的key
        key = f'{convert_language}_{dto.speech_role_name}_{dto.speech_rate}_{dto.speech_style}'
        file_detail = self.db.query(FileDetail).filter_by(module='SPEECH_LANGUAGE_DEMO_VOICE', module_id=key).first()
        if file_detail:
            # 检查文件是否存在，只有文件存在情况下才进行返回
            if os.path.exists(f'{Config.TEMP_SAVE_FILE_PATH}/{file_detail.file_name}'):
                return {'file': file_detail.file_name}

        # 如果language包含 '-' 则只需要取前面的部分
        speech_content = language_demo_map[convert_language]
        if not speech_content:
            raise ParameterIncorrectException('不支持的语言')
        # 调用speech组件，将speech_content转换成语音文件
        filename = f'{key}.wav'
        full_file_name = f'{Config.TEMP_SAVE_FILE_PATH}/{filename}'
        speech_component.speech(speech_content, full_file_name, voice_name=dto.speech_role_name,
                                speech_rate=dto.speech_rate, feel=dto.speech_style, targetLang=dto.language)
        file_detail = FileDetail(id=short_uuid(), file_path=filename,
                                 module='SPEECH_LANGUAGE_DEMO_VOICE', file_name=filename,
                                 module_id=key,
                                 file_ext='wav',
                                 created_by=account_id)
        self.db.add(file_detail)
        self.db.commit()
        self.db.flush()
        return {'file': file_detail.file_name}

    def message_speech(self, dto: TransformSpeechDTO, account_id: str):
        """文字转语音"""
        file_detail = self.db.query(FileDetail).filter(FileDetail.module == 'SPEECH_VOICE',
                                                       FileDetail.module_id == dto.message_id) \
            .order_by(FileDetail.create_time.desc()).first()
        if not file_detail:
            # 如果没有，就生成一个
            message = self.db.query(MessageEntity).filter_by(id=dto.message_id).first()
            # 获取信息对应的message_session信息，获取对应的配置
            session = self.db.query(MessageSessionEntity).filter_by(id=message.session_id).first()
            filename = f'{short_uuid("FILE")}.wav'
            full_file_name = f'{Config.TEMP_SAVE_FILE_PATH}/{filename}'

            speech_component.speech(message.content, full_file_name, voice_name=session.speech_role_name,
                                    speech_rate=session.speech_rate, feel=session.speech_style,
                                    targetLang=session.language)
            file_detail = FileDetail(id=short_uuid(), file_path=filename,
                                     module='SPEECH_VOICE', file_name=filename,
                                     module_id=dto.message_id,
                                     file_ext='wav',
                                     created_by=account_id)
            self.db.add(file_detail)
            message.file_name = filename
            self.db.commit()
            self.db.flush()
        return {'file': file_detail.file_name}

    def check_user_current_day_limit(self, account_id: str, usage_type: AccountUsageType):
        """普通用户需要查出当天使用量并进行比较"""

        # 获取用户当天的使用量
        if usage_type == AccountUsageType.CHAT:
            day_count = self.get_user_current_day_system_message_count(account_id)
            limit = Config.MAX_DAY_SYSTEM_MESSAGE_COUNT
            message = '今天的消息数已经超过了限制'
        elif usage_type == AccountUsageType.SPEECH:
            day_count = self.get_user_current_day_speech_count(account_id)
            limit = Config.MAX_DAY_SPEECH_COUNT
            message = '今天的语音使用已经超过了限制'
        elif usage_type == AccountUsageType.TRANSFORM:
            day_count = self.get_user_current_day_transform_count(account_id)
            limit = Config.MAX_DAY_TEXT_TO_VOICE_COUNT
            message = '今天的语音转换已经超过了限制'
        elif usage_type == AccountUsageType.PROMPT:
            day_count = self.get_user_current_day_prompt_count(account_id)
            limit = Config.MAX_DAY_PROMPT_COUNT
            message = '今天的提示数量已经超过了限制'
        else:
            raise Exception('不支持的usage_type')

        if day_count >= limit:
            raise UserAccessDeniedException(message)
        return True

    def check_user_session_limit(self, account_id: str):
        if self.get_session_count(account_id) >= 10:
            raise UserAccessDeniedException('一个用户最多创建10个会话')

    def __translate_content(self, content: str, target_language: str):
        """对内容进行翻译"""
        messages = [{"role": "system",
                     "content": 'You are a translation engine that can only translate text and cannot interpret it, ensuring that the translation is clear, concise, and coherent.'},
                    {"role": "user",
                     "content": f'Please translate the following text into {target_language} Simplified: {content}'}]
        result = self.__invoke_chat(messages)
        return result

    def __create_session(self, account_id: str, content: str):
        """创建一个新的session"""
        add_session = MessageSessionEntity(id=short_uuid('SESSION'), account_id=account_id, name=content)
        session_id = add_session.id
        self.db.add(add_session)
        return session_id

    def __add_account_message(self, account_id: str, session_id: str, content: str,
                              file_name: str = None):
        """添加用户消息"""
        message = MessageEntity(
            id=short_uuid('MSG'),
            account_id=account_id,
            sender=account_id,
            session_id=session_id,
            receiver=MESSAGE_SYSTEM,
            type=MessageType.ACCOUNT.value,
            content=content,
            file_name=file_name,
            length=len(content))
        self.db.add(message)
        self.db.commit()
        self.db.flush()
        self.__refresh_session_message_count(session_id)
        return message

    def __convert_session_model(self, session: MessageSessionEntity):
        return {'id': session.id, 'gender': session.gender, 'name': session.name, 'scene': session.scene,
                'speech_role_name': session.speech_role_name, 'language': session.language,
                'speech_rate': session.speech_rate, 'speech_style': session.speech_style,
                'scene_content': session.scene_content, 'message_count': session.message_count,
                'teacher_avatar': session.teacher_avatar, 'create_time': date_to_str(session.create_time),
                'friendly_time': friendly_time(date_to_str(session.create_time))}

    def __add_system_message(self, session_id, account_id: str, content: str) -> MessageEntity:
        """添加系统消息"""
        add_message = MessageEntity(
            id=short_uuid('MSG'),
            account_id=account_id,
            sender=MESSAGE_SYSTEM,
            session_id=session_id,
            receiver=account_id,
            type=MessageType.SYSTEM.value,
            content=content,
            length=len(content))
        self.db.add(add_message)
        self.db.commit()
        self.db.flush()
        self.__refresh_session_message_count(session_id)
        return add_message

    def __refresh_session_message_count(self, session_id: str):
        """刷新session的消息数量, 需要排除is_deleted为1的数据"""
        count = self.db.query(MessageEntity).filter(MessageEntity.session_id == session_id,
                                                    MessageEntity.is_deleted == 0).count()
        self.db.query(MessageSessionEntity).filter(MessageSessionEntity.id == session_id).update(
            {'message_count': count})
        self.db.commit()
        self.db.flush()

    def __invoke_chat(self, messages: List[Dict]):
        """调用chat gpt"""
        invoke_chat_json = chat_gpt_component.invoke_chat(ChatGPTInvokeDTO(messages=messages, max_tokens=300),
                                                          ApiKeyModel(organization=Config.CHAT_GPT_ORGANIZATION,
                                                                      api_key=Config.CHAT_GPT_KEY))
        invoke_result = invoke_chat_json['data']

        return invoke_result
