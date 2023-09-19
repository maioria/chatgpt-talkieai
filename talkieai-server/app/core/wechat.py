import requests


class WeChatComponent:
    # 构造方法设置 AppID 和 AppSecret
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret

    # 获取微信用户下头像及用户信息
    def get_user_info(self, code):
        url = f'https://api.weixin.qq.com/sns/jscode2session?appid={self.app_id}&secret={self.app_secret}&js_code={code}&grant_type=authorization_code'
        response = requests.get(url)
        data = response.json()
        print(data)
        # 检查返回的数据是否包含 OpenID 和 SessionKey
        if 'openid' in data and 'session_key' in data:
            return {
                'openid': data['openid'],
                'session_key': data['session_key']
            }
        else:
            return None
