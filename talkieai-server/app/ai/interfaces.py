from app.ai.models import *
from abc import ABC, abstractmethod
from typing import List, Dict
import json
import time
from pydantic import BaseModel
from abc import ABC, abstractmethod

from app.ai.models import *
from app.core.logging import logging

default_prompt_dict = {
    ChatType.TRANSLATE: 'You are a translation engine that can only translate text and cannot interpret it, ensuring that the translation is clear, concise, and coherent.',
    ChatType.GRAMMAR_ANALYSIS:'提供一段内容，只需要简洁快速的用中文返回这段内容中的语法错误，再根据提供的语言提供一句推荐示例，要求数据格式为json，语法是否错误放在属性isCorrect中，错误原因放在errorReason中，修正后的正确示例放在correctContent中，推荐示例放在better中，正确示例与推荐示例的语言要使用{language}',
    ChatType.WORD_DETAIL:'提供一个单词，只需要简洁快速的用中文返回这个单词的音标与翻译，要求数据格式为json，音标放在属性phonetic中，音标的前后要加上"/"，翻译放在translation中， 这个单词是"{word}"',
    ChatType.GREETING: 'You need to greet with {language} simplified.',
    ChatType.CHAT: 'I want you to act as an {language} speaking partner and improver, your name is $name. No matter what language I speak to you, you need to reply me in {language}. I hope you keep your responses clean and limit your responses to 80 characters. I hope you will ask me a question from time to time in your reply. Now let\'s start practicing. Remember, I want you reply me in {language} and your name is {name} and do not respond with any other information about yourself.'
}

class ChatAI(ABC):
    @abstractmethod
    def invoke_message(self, dto: MessageParams) -> Dict:
        """ 聊天 """
        pass

    @abstractmethod
    def invoke_translate(self, dto: TranslateParams) -> Dict:
        """ 翻译 """
        pass

    @abstractmethod
    def invoke_greet(self, dto: GreetParams) ->Dict:
        """ 打招呼 """
        pass

    @abstractmethod
    def invoke_grammar_analysis(self, dto: GrammarAnalysisParams) -> Dict:
        """ 语法分析 """
        pass

    @abstractmethod
    def invoke_prompt_sentence(self, dto: PromptSentenceParams) -> Dict:
        """ 为用户提示句子 """
        pass

    @abstractmethod
    def invoke_word_detail(self, dto: WordDetailParams) -> Dict:
        """ 单词详情 """
        pass

    def get_type_prompt(self, type: ChatType, type_params: Dict) -> str:
        # 获取default_prompt_dict对应类型的值，加上params赋值输出结果
        return default_prompt_dict[type].format(**type_params)

    
class MessageInvokeDTO(BaseModel):
    messages: List[Dict]


class MessageBaseAI(ChatAI):
    """不支持system的message"""
    def invoke_message(self, dto: MessageParams) -> Dict:
        logging.info(f"request_params:{dto.dict()}")
        system_message = self.get_type_prompt(ChatType.CHAT, {'language': dto.language, 'name': dto.name})
        # 百度接口没有system， 需要把system_message做为user角色放在第一句做为prompt
        messages = [
            {"role": "user", "content": system_message},
            {"role": "assistant", "content": "yes"},
        ]
        # 处理dto.messages 奇数位必须为assistant， 偶数位必须为user，如果对象不匹配，则进行移除
        insert_message_type = "user"
        for index, message in enumerate(dto.messages):
            if message["role"] == insert_message_type:
                messages.append(message)

                if insert_message_type == "user":
                    insert_message_type = "assistant"
                else:
                    insert_message_type = "user"
        invoke_dto = MessageInvokeDTO(messages=messages)
        return self._original_invoke_chat(invoke_dto)

    def invoke_translate(self, dto: TranslateParams) -> Dict:
        logging.info(f"request_params:{dto.dict()}")
        messages = [
            {"role": "user", "content": f'我希望你能充当{dto.target_language}翻译。我将用任何语言与你交谈，你将检翻译它。我的第一句话是： {dto.content}'}
        ]
        invoke_dto = MessageInvokeDTO(messages=messages)
        return self._original_invoke_chat(invoke_dto)

    def invoke_greet(self, params: GreetParams) -> Dict:
        logging.info(f"request_params:{params.dict()}")
        messages = [
            {"role": "user", "content": f'你需要使用标识为 {params.language} 的语言来打个招呼，10字左右.'}
        ]
        
        invoke_dto = MessageInvokeDTO(messages=messages)
        return self._original_invoke_chat(invoke_dto)

    def invoke_grammar_analysis(self, params: GrammarAnalysisParams) -> Dict:
        logging.info(f"request_params:{params.dict()}")
        messages = [
            {"role": "user", "content": f'请提供一段内容，只需要简洁快速的用中文返回这段内容中的语法错误，再根据提供的语言提供一句推荐示例，要求数据格式为json，无任何转义字符，可直接被程序正常序列化，语法是否错误放在属性isCorrect中，错误原因放在errorReason中，修正后的正确示例放在correctContent中，推荐示例放在better中，正确示例与推荐示例的语言要使用{params.language},提供内容是:{params.content}'}
        ]
        invoke_dto = MessageInvokeDTO(messages=messages)
        return self._original_invoke_chat(invoke_dto)

    def invoke_prompt_sentence(self, params: PromptSentenceParams) -> Dict:
        logging.info(f"request_params:{params.dict()}")
        system_content = "下面是一场对话\n"
        for message in reversed(params.messages):
            if message['role'].lower() == 'user':
                system_content = system_content + f"用户: {message['content']}\n"
            else:
                system_content = system_content + f"AI: {message['content']}\n"
        system_content = (
            system_content
            + "现在你需要做为一个用户来回答下一句话，只是答复不可以有提供帮助与提问问题的意思，要求给出3个不同答复，json数组格式,item中就是字符串，不可以使用对象，语言使用"
            + params.language
        )
        invoke_dto = MessageInvokeDTO(messages=[{"role": "user", "content": system_content}])
        return self._original_invoke_chat(invoke_dto)

    def invoke_word_detail(self, params: WordDetailParams) -> Dict:
        logging.info(f"request_params:{params.dict()}")
        messages = [
            {"role": "user", "content": f'提供一个单词，只需要简洁快速的用中文返回这个单词的音标与翻译，要求数据格式为json，音标放在属性phonetic中，音标的前后要加上"/"，翻译放在translation中， 这个单词是"{params.word}"'}
        ]
        invoke_dto = MessageInvokeDTO(messages=messages)
        return self._original_invoke_chat(invoke_dto)    

    @abstractmethod
    def _original_invoke_chat(self, dto: MessageInvokeDTO):
        pass
    

class SystemBaseAI(ChatAI):
    """类似于chatgpt 可以配置 system"""
    def invoke_message(self, dto: MessageParams) -> Dict:
        logging.info(f"request_params:{dto.dict()}")
        system_message = self.get_type_prompt(ChatType.CHAT, {'language': dto.language, 'name': dto.name})
        # 百度接口没有system， 需要把system_message做为user角色放在第一句做为prompt
        messages = [
            {"role": "system", "content": system_message}
        ]
        # 处理dto.messages 奇数位必须为assistant， 偶数位必须为user，如果对象不匹配，则进行移除
        insert_message_type = "user"
        for index, message in enumerate(dto.messages):
            if message["role"] == insert_message_type:
                messages.append(message)

                if insert_message_type == "user":
                    insert_message_type = "assistant"
                else:
                    insert_message_type = "user"
        invoke_dto = MessageInvokeDTO(messages=messages)
        return self._original_invoke_chat(invoke_dto)

    def invoke_translate(self, dto: TranslateParams) -> Dict:
        logging.info(f"request_params:{dto.dict()}")
        messages = [
            {"role": "user", "content": f'我希望你能充当{dto.target_language}翻译。我将用任何语言与你交谈，你将检翻译它。我的第一句话是： {dto.content}'}
        ]
        invoke_dto = MessageInvokeDTO(messages=messages)
        return self._original_invoke_chat(invoke_dto)

    def invoke_greet(self, params: GreetParams) -> Dict:
        logging.info(f"request_params:{params.dict()}")
        messages = [
            {"role": "user", "content": f'你需要使用标识为 {params.language} 的语言来打个招呼，10字左右.'}
        ]
        
        invoke_dto = MessageInvokeDTO(messages=messages)
        return self._original_invoke_chat(invoke_dto)

    def invoke_grammar_analysis(self, params: GrammarAnalysisParams) -> Dict:
        logging.info(f"request_params:{params.dict()}")
        messages = [
            {"role": "user", "content": f'请提供一段内容，只需要简洁快速的用中文返回这段内容中的语法错误，再根据提供的语言提供一句推荐示例，要求数据格式为json，无任何转义字符，可直接被程序正常序列化，语法是否错误放在属性isCorrect中，错误原因放在errorReason中，修正后的正确示例放在correctContent中，推荐示例放在better中，正确示例与推荐示例的语言要使用{params.language},提供内容是:{params.content}'}
        ]
        invoke_dto = MessageInvokeDTO(messages=messages)
        return self._original_invoke_chat(invoke_dto)

    def invoke_prompt_sentence(self, params: PromptSentenceParams) -> Dict:
        logging.info(f"request_params:{params.dict()}")
        system_content = "下面是一场对话\n"
        for message in reversed(params.messages):
            if message['role'].lower() == 'user':
                system_content = system_content + f"用户: {message['content']}\n"
            else:
                system_content = system_content + f"AI: {message['content']}\n"
        system_content = (
            system_content
            + "现在你需要做为一个用户来回答下一句话，只是答复不可以有提供帮助与提问问题的意思，要求给出3个不同答复，json数组格式,item中就是字符串，不可以使用对象，语言使用"
            + params.language
        )
        invoke_dto = MessageInvokeDTO(messages=[{"role": "user", "content": system_content}])
        return self._original_invoke_chat(invoke_dto)

    def invoke_word_detail(self, params: WordDetailParams) -> Dict:
        logging.info(f"request_params:{params.dict()}")
        messages = [
            {"role": "user", "content": f'提供一个单词，只需要简洁快速的用中文返回这个单词的音标与翻译，要求数据格式为json，音标放在属性phonetic中，音标的前后要加上"/"，翻译放在translation中， 这个单词是"{params.word}"'}
        ]
        invoke_dto = MessageInvokeDTO(messages=messages)
        return self._original_invoke_chat(invoke_dto)    

    @abstractmethod
    def _original_invoke_chat(self, dto: MessageInvokeDTO):
        pass