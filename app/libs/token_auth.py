

# 编写一个验证token的装饰器

from flask_httpauth import HTTPBasicAuth

from flask import current_app, g, request
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, \
          SignatureExpired

from collections import namedtuple

from app.libs.erro_code import AuthFailed, Forbidden
from app.libs.scope import is_in_scope

auth = HTTPBasicAuth()

User = namedtuple('User', ['uid', 'ac_type', 'scope'])

# @auth.verify_password
# def verify_password(account, password):

#   # 需要在HTTP请求的头部设置一个固定的键值对
#   # key=Authorization,value=basic base64(account:psd)
#   #    imwl@live.com:12345678   编码后 aW13bEBsaXZlLmNvbToxMjM0NTY3OA==
#   #  key=Authorization,value=basic aW13bEBsaXZlLmNvbToxMjM0NTY3OA==
#     return True

@auth.verify_password
def verify_password(token, password):
    user_info =  verify_auth_token(token) # token 赋值给 user_info
    if not user_info:
        return False
    else:
        g.user = user_info  # g 变量 ,代理模式
        return True


def verify_auth_token(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)   # 解密 token
    # token不合法抛出的异常
    except BadSignature:
        raise AuthFailed(msg='token is valid', erro_code=1002)
    # token过期抛出的异常
    except SignatureExpired:
        raise AuthFailed(msg='token is expired', erro_code=1003)

    uid = data['uid']
    ac_type = data['type']   # 生成令牌的时候写入了 uid ac_type
    scope = data['scope']
    # 也可在这拿到当前request的视图函数
    allow = is_in_scope(scope ,request.endpoint) # request.endpoint  拿到当前视图函数的endpoint
    if not allow:
        raise Forbidden()
    return User(uid, ac_type, scope)   # 定义对象式 接口返回回去 ,scope 先返回为空字符串