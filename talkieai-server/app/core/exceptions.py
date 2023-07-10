"""全局异常类"""
class UserAccessDeniedException(Exception):
    """用户资源访问受限exception"""
    pass


class UserPasswordIncorrectException(Exception):
    """用户密码不正确"""
    pass


class ParameterIncorrectException(Exception):
    """参数不正确"""
    pass
