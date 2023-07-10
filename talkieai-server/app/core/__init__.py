from app.config import Config
from app.core.auth import Auth
from fastapi import Header

from app.core.speech import AzureSpeechComponent

# auth 配置
auth = Auth(Config.TOKEN_SECRET, Config.ALGORITHM, Config.DECODED_TOKEN_IAT_KEY, Config.TOKEN_EXPIRE_TIME,
            Config.DECODED_TOKEN_USER_KEY)


def get_current_account(x_token: str = Header(None)):
    return auth.get_current_account(x_token)

#speech 配置
speech_component = AzureSpeechComponent(Config.AZURE_KEY, "eastasia")