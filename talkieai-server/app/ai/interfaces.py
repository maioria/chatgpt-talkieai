from app.ai.models import *
from abc import ABC, abstractmethod
from typing import List, Dict
from abc import ABC, abstractmethod
from dataclasses import dataclass
from app.ai.models import *


@dataclass
class MessageInvokeDTO:
    messages: List[Dict]
    temperature: float = 0.5
    max_tokens: int = 300


@dataclass
class FunctionInvokeDTO:
    function: Dict
    messages: List[Dict]
    temperature: float = 0.5
    max_tokens: int = 300


class ChatAI(ABC):
    @abstractmethod
    def invoke_message(self, dto: MessageParams) -> AIMessageResult:
        """聊天"""
        pass

    @abstractmethod
    def invoke_translate(self, dto: TranslateParams) -> str:
        """翻译"""
        pass

    @abstractmethod
    def invoke_greet(self, dto: GreetParams) -> str:
        """打招呼"""
        pass

    @abstractmethod
    def invoke_grammar_analysis(
        self, dto: GrammarAnalysisParams
    ) -> AIGrammarAnalysisResult:
        """语法分析"""
        pass

    @abstractmethod
    def invoke_prompt_sentence(self, dto: PromptSentenceParams) -> str:
        """为用户提示句子"""
        pass

    @abstractmethod
    def invoke_word_detail(self, dto: WordDetailParams) -> AIWordDetailResult:
        """单词详情"""
        pass

    @abstractmethod
    def topic_invoke_greet(self, dto: TopicGreetParams) -> str:
        """场景 打招呼"""
        pass

    @abstractmethod
    def topic_invoke_message(self, dto: AITopicMessageParams) -> AITopicMessageResult:
        """场景 聊天"""
        pass

    @abstractmethod
    def topic_invoke_complete(self, dto: AITopicCompleteParams) -> AITopicCompleteResult:
        """场景 结束"""
        pass
