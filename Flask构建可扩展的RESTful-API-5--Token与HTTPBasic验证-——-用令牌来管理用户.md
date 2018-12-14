# 5.1 Token

### 1.Token概述

以下是网站登录和使用API登录的区别


![image](http://upload-images.jianshu.io/upload_images/14597179-16de41d674064a75?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240) 


与网站登录不同的是，网站登录将登录信息写入cookie存储在浏览器，而API只负责生成token发送给客户端，而客户端怎么存储有自己决定。

*   Token具有有效期
*   Token可以标示用户身份，如存储用户id

### 2.获取Token令牌

密码校验--app.models/user.py

```
from sqlalchemy import inspect, Column, Integer, String, SmallInteger, orm
from werkzeug.security import generate_password_hash, check_password_hash

from app.libs.erro_code import NotFound, AuthFailed
from app.models.base import Base , db #, MixinJSONSerializer
import datetime

class User(Base):
    id = Column(Integer, primary_key=True)
    email = Column(String(24), unique=True, nullable=False)
    nickname = Column(String(24), unique=True)
    auth = Column(SmallInteger, default=1)   # 做层级的标志
    _password = Column('password', String(100))

    def keys(self):
        return ['id', 'email', 'nickname', 'auth']

    @property               
    def password(self):
        return self._password   #  对密码的处理

    @password.setter
    def password(self, raw):
        self._password = generate_password_hash(raw)    #  对密码的处理

    @staticmethod
    def register_by_email(nickname, account, secret):
        with db.auto_commit():
            user = User()
            user.nickname = nickname
            user.email = account
            user.password = secret
            db.session.add(user)

    @staticmethod
    def verify(email, password):
        user = User.query.filter_by(email=email).first_or_404()   # 查询出当前用户
        if not user:
            raise NotFound(msg = 'user not found...')
        if not user.check_password(password):  # 检验密码
            raise AuthFailed()   #抛出异常
        return {'uid': user.id}  #成功，返回uid

    def check_password(self, raw):   # 密码检验
        if not self._password:
            return False
        return check_password_hash(self._password, raw)
```
返回token的试图函数，这里稍微破坏一下REST的规则，由于登录操作密码安全性较高，使用GET的话会泄漏
app\api\v1\token.py
```
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
                                None,
                                expiration=expiration)
    t = {
            'token': token.decode('utf-8')  # 因为是byte
        }
    return jsonify(t), 201  # 返回 json 字典

def generator_auth_token(uid, ac_type, scope=None,expiration=7200):
    """生成令牌  ，拿到uid,client类型，权限作用域，过期时间"""
    s = Serializer(current_app.config['SECRET_KEY'],expires_in=expiration)  # expires_in 生成令牌的有效期
    return s.dumps({
                    'uid': uid,
                    'type': ac_type.value
                })  # 将想写入的信息以字典形式写入令牌
```
app.setting.py

```

TOKEN_EXPIRATION = 30 * 24 * 3600

```
app\libs\erro_code.py
```
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

class NotFound(APIException):
    code = 404
    msg = 'the resource are not found O__O...'
    error_code = 1001


class AuthFailed(APIException):
    code = 401
    error_code = 1005
    msg = 'authorization failed'


class Forbidden(APIException):
    code = 403
    error_code = 1004
    msg = 'forbidden, not in scope'
```
注册到Blueprint
app\api\v1\__init__.py

```

from flask import Blueprint
from app.api.v1 import user, book ,client ,token

 #  创建一个Bluerint,把Redprint注册到Blueprint上，并传入Redprint一个前缀'/book
def create_blueprint_v1():
    bp_v1 = Blueprint('v1', __name__) 

    user.api.register(bp_v1)  # , url_prefix='/uesr')
    book.api.register(bp_v1)  # ,url_prefix='/book')
    client.api.register(bp_v1)
    token.api.register(bp_v1)
    return bp_v1
```

### 3.Token的用处

![成功拿到token](https://upload-images.jianshu.io/upload_images/14597179-00e4e57198ea8398.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
我们不可能让任何一个用户都来访问我们获取用户资料的接口，必须对这个加以控制，也就是说只有确定了身份的用户可以访问我们的接口。

如何对这个接口做保护呢？

当用户访问问的接口的时候，我们需要获取他传来的token并进行解析验证，只有token是合法的且没有过期，我们才允许访问。

由于每个需要验证token的试图函数都需要上面的业务逻辑，所以我们可以编写一个装饰器，以面向切面的方式统一处理，编写一个函数验证token，如果验证通过，我们就继续执行试图函数的方法，如果不通过，我们就返回一个自定义异常。

app.libs/token_auth.py

```
from flask_httpauth import HTTPBasicAuth


auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(account, password):
    pass
    

```
app/api/v1/user.py
```
from app.libs.redprint import Redprint
from app.libs.token_auth import auth

api = Redprint('user')
#@api.route('/get')  URL中不应该包含动词
@api.route('',methods = ['GET'])
@auth.login_required
def get_user():
    return 'get_user'
```

# 5.2 HTTPBasicAuth

### 1.HTTPBasicAuth基本原理

除了自定义发送账号和密码之外，HTTP这种协议本身就有多种规范，来允许我们来传递账号和密码。其中一种就是HTTPBasic

HTTPBasic：需要在HTTP请求的头部设置一个固定的键值对key=Authorization,value=basic base64(account:psd)

### 2.以BasicAuth方式来发送token

我们可以将token作为上面所说的账号account，而密码psd传递空值


![image](http://upload-images.jianshu.io/upload_images/14597179-a2e70aff0db906a6?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240) 





![image](http://upload-images.jianshu.io/upload_images/14597179-3cd26baf973aba35?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240) 




# 5.3 Token的发送与验证

### 1.验证token

```
auth = HTTPBasicAuth()
User = namedtuple('User', ['uid', 'ac_type', 'scope'])

@auth.verify_password
def verify_password(token, password):
user_info = verify_auth_token(token)
if not user_info:
return False
else:
g.user = user_info

return True

def verify_auth_token(token):
s = Serializer(current_app.config['SECRET_KEY'])
try:
data = s.loads(token)
# token不合法抛出的异常
except BadSignature:
raise AuthFailed(msg='token is valid', error_code=1002)
# token过期抛出的异常
except SignatureExpired:
raise AuthFailed(msg='token is expired', error_code=1003)
uid = data['uid']
ac_type = data['type']
return User(uid, ac_type, '')
```
### 2.视图函数的编写
```
@api.route('/<int:uid>', methods=['GET'])
@auth.login_required
def get_user(uid):
user = User.query.get_or_404(uid)
r = {
'nickname': user.nickname,
'email': user.email
}
return jsonify(r), 200
```
### 3.重写后的get_or_404,抛出自定义异常
```
def get_or_404(self, ident):
rv = self.get(ident)
if not rv:
raise NotFound()
return rv

def first_or_404(self):
rv = self.first()
if not rv:
raise NotFound()
return rv
```
### 4.获取令牌信息
```
@api.route('/secret', methods=['POST'])
def get_token_info():
"""获取令牌信息"""
form = TokenForm().validate_for_api()
s = Serializer(current_app.config['SECRET_KEY'])
try:
data = s.loads(form.token.data, return_header=True)
except SignatureExpired:
raise AuthFailed(msg='token is expired', error_code=1003)
except BadSignature:
raise AuthFailed(msg='token is invalid', error_code=1002)

r = {
'scope': data[0]['scope'],
'create_at': data[1]['iat'],
'expire_in': data[1]['exp'],
'uid': data[0]['uid']
}
return jsonify(r)
```
