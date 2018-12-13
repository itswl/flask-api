
from werkzeug.exceptions import HTTPException
# 自定义异常类

class ClientTypeErro(HTTPException):
    code = 400
    description = (
        'client is invalid'
    )