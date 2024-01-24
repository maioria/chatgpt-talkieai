from typing import List, Dict
import json
from pydantic import BaseModel

from app.ai.interfaces import *
from app.ai.models import *
from app.core.language import *
from app.core.logging import logging


class ZhipuInvokeDTO(BaseModel):
    messages: List[Dict]
    model: str
    temperature: int = 0.1


class ZhipuAIComponent(ChatAI):
    def __init__(self, api_key: str, model: str):
        from zhipuai import ZhipuAI

        self.client = ZhipuAI(api_key=api_key)
        self.model = model

    def invoke_greet(self, params: GreetParams) -> str:
        messages = [
            {"role": "user", "content": f"你需要使用标识为 {params.language} 的语言来打个招呼，10字左右."}
        ]

        invoke_dto = MessageInvokeDTO(messages=messages)
        return self._original_invoke_chat(invoke_dto)

    def topic_invoke_greet(self, params: TopicGreetParams) -> str:
        messages = [
            {
                "role": "user",
                "content": f"场景：{params.prompt}. 现在你需要打个招呼，20字左右.记住语言必须使用使用 {get_language_label_by_value(params.language)}，不可以使用其他语言 ",
            }
        ]

        invoke_dto = MessageInvokeDTO(messages=messages)
        return self._original_invoke_chat(invoke_dto)

    def invoke_message(self, dto: MessageParams) -> AIMessageResult:
        """与AI自由聊天"""
        language = dto.language
        system_message = (
            'The reply must be json, and format of json is {"message":"result of message","message_style":"must be one of the options '
            + f"{json.dumps(dto.styles, ensure_ascii=False)}"
            + '"}, '
            + f"The 'message_style'  within the square brackets . "
            + f"I want you to act as an {language} speaking partner and improver, your name is {dto.name}. "
            + f"No matter what language I speak to you, you need to reply me in {language}. "
            + f"I hope you will ask me a question from time to time in your reply "
        )

        messages = [{"role": "system", "content": system_message}]
        for message in dto.messages:
            messages.append(message)
        resp = self._original_invoke_chat(MessageInvokeDTO(messages=messages))
        # 检查resp是否是json格式，如果不json格式，就返回错误
        try:
            resp = json.loads(resp)
            result = AIMessageResult(
                message=resp["message"], message_style=resp["message_style"]
            )
        except Exception as e:
            logging.warn(f"resp不是json格式:{resp},request_params:{system_message}")
            result = AIMessageResult(message=resp, message_style=None)

        return result

    def topic_invoke_message(self, dto: AITopicMessageParams) -> AITopicMessageResult:
        """与AI自由聊天"""
        language = dto.language
        system_message = (
            f"Topic:{dto.prompt}.Please chat with me in this topic. If this conversation can be concluded or if the user wishes to end it, please return topic_completed=true."
            + 'The reply must be json, and format of json is {"message":"result of message","topic_completed":"Whether this topic has been completd.","message_style":"must be one of the options '
            + f"{json.dumps(dto.styles, ensure_ascii=False)}"
            + '"}, '
            + f"The 'message_style'  within the square brackets . "
            + f"I want you to act as an {language} speaking partner and improver, your name is {dto.name}. "
            + f"No matter what language I speak to you, you need to reply me in {language}. "
            + f"I hope you will ask me a question from time to time in your reply "
        )

        messages = [{"role": "system", "content": system_message}]
        for message in dto.messages:
            messages.append(message)

        resp = self._original_invoke_chat(MessageInvokeDTO(messages=messages))
        # 检查resp是否是json格式，如果不json格式，就返回错误
        try:
            resp = json.loads(resp)
            message_style = None
            # resp是否有message_style
            if "message_style" in resp:
                message_style = resp["message_style"]

            completed = False
            # resp是否有topic_completed
            if "topic_completed" in resp:
                completed = resp["topic_completed"] == "true"
            result = AITopicMessageResult(
                message=resp["message"],
                message_style=message_style,
                completed=completed,
            )
        except Exception as e:
            logging.warn(f"resp不是json格式:{resp},request_params:{system_message}")
            result = AITopicMessageResult(
                message=resp, completed=False, message_style=None
            )

        return result

    def topic_invoke_complete(
        self, dto: AITopicCompleteParams
    ) -> AITopicCompleteResult:
        """场景 结束"""
        system_content = "下面是一场对话\n"
        for message in dto.messages:
            if message.role.lower() == "system":
                system_content = system_content + f"AI: {message.content}\n"
            elif message.role.lower() == "account":
                system_content = system_content + f"用户: {message.content}\n"

        system_content = system_content + "下面是用户对话中需要实现的目标\n"
        for target in dto.targets:
            system_content = system_content + f"{target}\n"

        system_content = (
            system_content
            + "现在你需要计算出 <用户:> 所说的所有话中使用了多少单词数量（仅需要数字结果，重复单词不需要计算），对应后面的目标实现了多少个（仅需要数字结果），对用户的表达给出评分（满分100分，仅需要数字结果），还要给出300字以内的建议（包含中文讲解与英文示例），返回结果只需要有json格式,使用单词量放在words字段，目标实现数量放在targets字段，评分放在score字段，建议放在suggestion字段，不需要再额外的任何信息，记住，只需要统计<用户:>下的内容\n"
        )
        json_result = self._original_invoke_chat_json(
            MessageInvokeDTO(messages=[{"role": "user", "content": system_content}])
        )
        # 组装成AITopicCompleteResult返回
        return AITopicCompleteResult(
            targets=json_result["targets"],
            score=json_result["score"],
            words=json_result["words"],
            suggestion=json_result["suggestion"],
        )

    def invoke_translate(self, dto: TranslateParams) -> str:
        """翻译"""
        system_message = f"下面是段文本：'{dto.content}'   仅输出翻译成 {dto.target_language} 后的内容，不可以有其他介绍内容"
        invoke_dto = MessageInvokeDTO(
            messages=[{"role": "user", "content": system_message}]
        )
        resp = self._original_invoke_chat(invoke_dto)
        return resp

    def invoke_grammar_analysis(
        self, params: GrammarAnalysisParams
    ) -> AIGrammarAnalysisResult:
        messages = [
            {
                "role": "user",
                "content": f"检查内容是否存在语法错误(不需要检查符号的使用)，如果存在就用中文返回这段内容中的语法错误，再提供一句推荐示例，要求数据格式为json，无任何转义字符，可直接被程序正常序列化，语法是否错误放在属性isCorrect中，错误原因放在errorReason中，修正后的正确示例放在correctContent中，推荐示例放在better中，正确示例与推荐示例的语言要使用{params.language},错误原因使用中文. 提供内容是:{params.content}",
            }
        ]
        invoke_dto = MessageInvokeDTO(messages=messages)
        result_json = self._original_invoke_chat_json(invoke_dto)
        return AIGrammarAnalysisResult(
            is_correct=result_json["isCorrect"],
            error_reason=result_json["errorReason"],
            correct_content=result_json["correctContent"],
            better=result_json["better"],
        )

    def invoke_prompt_sentence(self, params: PromptSentenceParams) -> str:
        """ """
        logging.info(f"request_params:{params}")
        system_content = "下面是一场对话\n"
        for message in reversed(params.messages):
            if message["role"].lower() == "user":
                system_content = system_content + f"用户: {message['content']}\n"
            else:
                system_content = system_content + f"AI: {message['content']}\n"
        system_content = (
            system_content
            + "现在你需要做为一个用户来回答下一句话，不可以有提供帮助与提问问题的意思，返回内容不得包含 用户: 等其他介绍字眼，语言使用"
            + params.language
        )
        invoke_dto = MessageInvokeDTO(
            messages=[{"role": "user", "content": system_content}]
        )
        resp = self._original_invoke_chat(invoke_dto)
        return resp

    def invoke_word_detail(self, params: WordDetailParams) -> AIWordDetailResult:
        logging.info(f"request_dto:{params}")
        messages = [
            {
                "role": "user",
                "content": f'提供一个单词，只需要简洁快速的用中文返回这个单词的音标与翻译，要求数据格式为json，音标放在属性phonetic中，音标的前后要加上"/"，翻译放在translation中， 这个单词是"{params.word}"',
            }
        ]
        invoke_dto = MessageInvokeDTO(messages=messages)
        result_json = self._original_invoke_chat_json(invoke_dto)
        return AIWordDetailResult(
            phonetic=result_json["phonetic"], translation=result_json["translation"]
        )

    def _original_invoke_chat(self, dto: MessageInvokeDTO):
        logging.info(f"request_params:{dto.__dict__}")
        # invoke_dto = ZhipuInvokeDTO(messages=dto.messages, model=self.model)
        resp = self.client.chat.completions.create(
            model=self.model, messages=dto.messages, stream=False
        )
        logging.info(f"response:{resp}")

        result = resp.choices[0].message.content
        # 去掉俩边的 “”
        result = result.strip('"')
        # 去掉json的转义字符
        result = result.replace('\\"', '"').replace("\\n", "\n").replace("\\", "")
        return result

    def _original_invoke_chat_json(self, dto: MessageInvokeDTO):
        logging.info(f"request_params:{dto.__dict__}")
        invoke_dto = ZhipuInvokeDTO(messages=dto.messages, model=self.model)
        resp = self.client.chat.completions.create(**invoke_dto.__dict__)
        logging.info(f"response:{resp}")

        result = resp.choices[0].message.content
        # 如果格式为类似markdown的 ```json\n{}\n```，就去掉前后的 ```json\n 与 \n```
        if result.startswith("```json\n") and result.endswith("\n```"):
            result = result.replace("```json\n", "").replace("\n```", "")
        # 去掉俩边的 “”
        result = result.strip('"')
        # 去掉json的转义字符
        result = result.replace('\\"', '"').replace("\\n", "\n").replace("\\", "")
        return json.loads(result)
