import time
import jwt
from fastapi import HTTPException



class Auth:
    def __init__(self, token_secret: str, algorithm: str, decoded_token_iat_key: str, expire_time: int,
                 decoded_token_user_key: str):
        self.token_secret = token_secret
        self.algorithm = algorithm
        self.expire_time = expire_time
        self.decoded_token_iat_key = decoded_token_iat_key
        self.decoded_token_user_key = decoded_token_user_key

    def init_token(self, name: str, id: str) -> str:
        return jwt.encode({
            'sub': id,
            'iat': int(time.time()),
            'name': name
        }, self.token_secret, algorithm=self.algorithm)

    def get_current_account(self, x_token: str) -> str:
        """Get user info from x_token"""
        if not x_token:
            raise HTTPException(status_code=401, detail="X-Token header is missing")
        try:
            decoded_token = jwt.decode(x_token, self.token_secret, algorithms=[self.algorithm])
        except jwt.PyJWTError:
            print(jwt.PyJWTError)
            raise HTTPException(status_code=401, detail="Invalid token")
        # Check Whether the token expired
        iat = decoded_token.get(self.decoded_token_iat_key)
        """Check whether the token is expired"""
        delta = int((time.time() - iat) / 60)
        if delta > self.expire_time:
            raise HTTPException(status_code=401, detail="Token has expired")
        account_id = decoded_token.get(self.decoded_token_user_key)
        if not account_id:
            raise HTTPException(status_code=401, detail="User not found in token")
        return account_id



