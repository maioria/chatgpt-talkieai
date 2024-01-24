from app.config import Config
from app.ai.impl.zhipu_ai import ZhipuAIComponent
from app.ai.impl.chat_gpt_ai import ChatGPTAI
if Config.AI_SERVER=='CHAT_GPT':
    chat_ai = ChatGPTAI(api_key=Config.CHAT_GPT_KEY, base_url=Config.CHAT_GPT_PROXY, model=Config.CHAT_GPT_MODEL)
elif Config.AI_SERVER=='ZHIPU':
    chat_ai = ZhipuAIComponent(api_key=Config.ZHIPU_AI_API_KEY, model=Config.ZHIPU_AI_MODEL)
else:
    raise Exception('AI_SERVER配置错误，只能配置为CHAT_GPT或ZHIPU')