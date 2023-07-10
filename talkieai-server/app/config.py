import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # 是否开启SQL语句打印
    SQL_ECHO: bool = os.getenv('SQL_ECHO').lower() == 'true'
    # JWT配置
    TOKEN_SECRET = os.getenv('TOKEN_SECRET')
    # JWT算法
    ALGORITHM = 'HS256'
    # JWT用户key
    DECODED_TOKEN_USER_KEY = "sub"
    # JWT签发时间key
    DECODED_TOKEN_IAT_KEY = "iat"
    # JWT过期时间
    TOKEN_EXPIRE_TIME = int(os.getenv("TOKEN_EXPIRE_TIME"))
    # 数据库连接信息，需要判断不能为空
    SQLALCHEMY_DATABASE_URL: str = os.getenv('DATABASE_URL')
    # API前缀
    API_PREFIX = os.getenv('API_PREFIX', '/api')
    # 文件上传路径
    TEMP_SAVE_FILE_PATH = os.getenv('TEMP_SAVE_FILE_PATH')
    # 微软语音
    AZURE_KEY = os.getenv('AZURE_KEY')
    # ChatGPT Organization
    CHAT_GPT_ORGANIZATION = os.getenv('CHAT_GPT_ORGANIZATION')
    # ChatGPT Key
    CHAT_GPT_KEY = os.getenv('CHAT_GPT_KEY')
    # Remote ChatGPT Server
    CHAT_GPT_SERVER = os.getenv('CHAT_GPT_SERVER')
    # 每天最多消息数量
    MAX_DAY_SYSTEM_MESSAGE_COUNT = int(os.getenv('MAX_DAY_SYSTEM_MESSAGE_COUNT'))
    # 每天最多提示数量
    MAX_DAY_PROMPT_COUNT = int(os.getenv('MAX_DAY_PROMPT_COUNT'))
    # 每天最多语音数量
    MAX_DAY_SPEECH_COUNT = int(os.getenv('MAX_DAY_SPEECH_COUNT'))
    # 每天最多文本转语音数量
    MAX_DAY_TEXT_TO_VOICE_COUNT = int(os.getenv('MAX_DAY_TEXT_TO_VOICE_COUNT'))
