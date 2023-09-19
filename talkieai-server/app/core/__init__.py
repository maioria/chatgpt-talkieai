from fastapi import Header

from app.config import Config
from app.core.auth import Auth
from app.core.wechat import WeChatComponent

auth = Auth(Config.TOKEN_SECRET, Config.ALGORITHM, Config.DECODED_TOKEN_IAT_KEY, Config.TOKEN_EXPIRE_TIME,
            Config.DECODED_TOKEN_USER_KEY)


def get_current_account(x_token: str = Header(None)):
    return auth.get_current_account(x_token)

# 微信小程序登录
wechat_component = WeChatComponent(Config.WECHAT_APP_ID, Config.WECHAT_APP_SECRET)