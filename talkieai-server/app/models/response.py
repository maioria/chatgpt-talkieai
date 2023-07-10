from pydantic import BaseModel


class ApiResponse:
    def __init__(self, code: str = '200', status: str = 'SUCCESS', data=None, message: str = 'success'):
        self.code = code
        self.status = status
        self.data = data
        self.message = message
