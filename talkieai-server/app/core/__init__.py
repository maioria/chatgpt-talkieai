from fastapi import Header

from app.config import Config
from app.core.auth import Auth

auth = Auth(Config.TOKEN_SECRET, Config.ALGORITHM, Config.DECODED_TOKEN_IAT_KEY, Config.TOKEN_EXPIRE_TIME,
            Config.DECODED_TOKEN_USER_KEY)


def get_current_account(x_token: str = Header(None), x_token_query: str = None):
    if x_token_query:
        return auth.get_current_account(x_token_query)
    return auth.get_current_account(x_token)
