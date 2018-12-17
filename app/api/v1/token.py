
from app.libs.redprint import Redprint

from flask import current_app
from app.libs.enums import ClientTypeEnum
from app.models.user import User
from app.validators.forms import ClientForm
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from flask import jsonify


api = Redprint('token') # 实例化一个Redprint

@api.route('', methods=['POST'])  # 路由注册
# 返回token的试图函数，这里稍微破坏一下REST的规则，由于登录操作密码安全性较高，使用GET的话会泄漏
def get_token():
    form = ClientForm().validate_for_api()   # 同注册过程，不同client 区分
    promise = {
        ClientTypeEnum.USER_EMAIL: User.verify,  #验证 # 在 user中编写 verify
        # ClientTypeEnum.USER_MINA: __register_user_by_MINA 
    }
    # 拿到用户信息
    identity = promise[form.type.data](
        form.account.data,
        form.secret.data
    )

    # 调用函数生成token
    expiration = current_app.config['TOKEN_EXPIRATION']  #过期时间
    token = generator_auth_token(identity['uid'],
                                form.type.data,
                                identity['scope'],
                                expiration=expiration)
    t = {
            'token': token.decode('ascii')  # 因为是byte
        }
    return jsonify(t), 201  # 返回 json 字典

def generator_auth_token(uid, ac_type, scope=None,expiration=7200):
    """生成令牌  ，拿到uid,client类型，权限作用域，过期时间"""
    s = Serializer(current_app.config['SECRET_KEY'],expires_in=expiration)  # expires_in 生成令牌的有效期
    return s.dumps({
                    'uid': uid,
                    'type': ac_type.value,
                    'scope': scope
                })  # 将想写入的信息以字典形式写入令牌