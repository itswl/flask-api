
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

class DeleteSuccess(Success):
    code = 202
    erro_code = 1

class ServerError(APIException):
    code = 500
    msg  = 'sorry,we made a mistaake'
    erro_code = 999

class NotFound(APIException):
    code = 404
    msg = 'the resource are not found O__O...'
    erro_code = 1001


class AuthFailed(APIException):
    code = 401
    erro_code = 1005
    msg = 'authorization failed'


class Forbidden(APIException):
    code = 403
    erro_code = 1004
    msg = 'forbidden, not in scope'

class DuplicateGift(APIException):
    code = 400
    erro_code = 2001
    msg = 'the current book has already in gift'