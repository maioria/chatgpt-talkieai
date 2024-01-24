from typing import List, Dict
from dataclasses import dataclass, field


@dataclass
class MessageItemParams:
    role: str
    content: str

@dataclass
class MessageParams:
    language: str
    name: str
    messages: List[Dict]
    styles: List[str]
    temperature: float = 0.5
    max_tokens: int = 300


@dataclass
class AITopicMessageParams:
    language: str
    speech_role_name: str
    prompt: str
    name: str
    messages: List[Dict] = field(default_factory=list)
    styles: List[str] = field(default_factory=list)
    temperature: float = 0.5
    max_tokens: int = 300


@dataclass
class AITopicCompleteParams:
    language: str
    targets: List[str] = field(default_factory=list)
    messages: List[MessageItemParams] = field(default_factory=list)

@dataclass
class AITopicCompleteResult:
    targets: str
    score: str 
    words: int 
    suggestion: str 

@dataclass
class AIMessageResult:
    message: str
    message_style: str | None


@dataclass
class AITopicMessageResult:
    message: str
    message_style: str | None
    completed: bool


@dataclass
class TranslateParams:
    target_language: str
    content: str


@dataclass
class GreetParams:
    language: str


@dataclass
class GrammarAnalysisParams:
    language: str
    content: str


@dataclass
class AIGrammarAnalysisResult:
    is_correct: bool
    error_reason: str
    correct_content: str
    better: str


@dataclass
class PromptSentenceParams:
    language: str
    messages: List[Dict]


@dataclass
class WordDetailParams:
    word: str


@dataclass
class AIWordDetailResult:
    phonetic: str
    translation: str


@dataclass
class TopicGreetParams:
    language: str
    prompt: str