
# from werkzeug.exceptions import HTTPException
# # 自定义异常类

# class ClientTypeErro(HTTPException):
#     code = 400
#     description = (
#         'client is invalid'
#     )
  

# ↑ 不再继承HTTPException

# ↓ 继承APIException
from app.libs.erro import APIException

class ClientTypeErro(APIException):
    code = 400
    msg = 'client is invalid'
    erro_code = 1006


class ParameterException(APIException):
    code = 400
    msg = 'invalid parameter'
    erro_code = 1000

# 将成功返回也当作一中 APIException，来优化代码
class Success(APIException):
    code = 201
    msg = 'ok'
    erro_code = 0

class ServerError(APIException):
    code = 500
    msg  = 'sorry,we made a mistaake'
    erro_code = 999