
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
    description = (
        'client is invalid'
    )