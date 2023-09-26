import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    AI_NAME = os.getenv('AI_NAME')
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
    # WeChat AppID
    WECHAT_APP_ID = os.getenv('WECHAT_APP_ID')
    # WeChat AppSecret
    WECHAT_APP_SECRET = os.getenv('WECHAT_APP_SECRET')
    # 微信服务基础地址
    WE_CHAT_SERVER_URL = os.getenv('WE_CHAT_SERVER_URL')
    # AI
    AI_SERVER = os.getenv('AI_SERVER')
    # 百度AI配置
    BAIDU_AI_API_KEY = os.getenv('BAIDU_AI_API_KEY')
    BAIDU_AI_SECRET_KEY = os.getenv('BAIDU_AI_SECRET_KEY')
    BAIDU_AI_MODEL = os.getenv('BAIDU_AI_MODEL')

    # 智谱AI配置
    ZHIPU_AI_API_KEY = os.getenv('ZHIPU_AI_API_KEY')
    ZHIPU_AI_MODEL = os.getenv('ZHIPU_AI_MODEL')

    # Remote ChatGPT Server
    CHAT_GPT_SERVER = os.getenv('CHAT_GPT_SERVER')