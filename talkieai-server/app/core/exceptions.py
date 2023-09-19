# 用户资源访问受限exception
class UserAccessDeniedException(Exception):
    pass


# 用户密码不正确
class UserPasswordIncorrectException(Exception):
    pass


# 参数不正确
class ParameterIncorrectException(Exception):
    pass
