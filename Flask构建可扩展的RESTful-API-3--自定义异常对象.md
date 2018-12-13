# 3.1 关于用户的思考
 
 不管是网站也好，还是API也好，我们都逃脱不了用户这个概念，我们下面就要来讨论用户的相关操作
 

 对于用户而言，第一件事情，我们就要完成用户注册的操作，说到注册用户，我们想到，可以在视图函数文件中增加一个注册用户的视图函数--create_user，并且我们会在其中接受账号和密码，来完成用户的注册，这个逻辑是通常意义上的用户的概念。
 

 普通用户：使用鱼书的人相对于鱼书来说，就是用户；我们相对于QQ和微信，也是他的用户。
 

 但是我们在做API的时候，不能只考虑这些普通意义的用户，我们还要考虑一些特别的用户。例如：我们开发了一个向外提供数据的API，加入有一天，有一个公司，想使用我们的API开发他们自己的产品（小程序或者APP），这些其他的客户端，都是我们API的用户
 

根据以上的分析，我们可以得出几个结论：
对于API而言，再叫做用户就不太合适 ，我们更倾向于把人，第三方的产品等同于成为客户端（client）来代替User。
客户端的种类非常多，注册的形式就非常多。如对于普通的用户而言，就是账号和密码，但是账号和密码又可以分成，短信，邮件，社交用户。对于多种的注册形式，也不是所有的都需要密码，如小程序就不需要。
API和普通的业务系统是不一样的，他具有开发性和通用性。
因为注册的形式就非常多，所以我们不可能用万能的方式来解决。如果我们不能很好的处理多种多样的形式，我们的代码就会非常的杂乱

3.2 注册client
对于登录/注册这些比较重要的接口，我们建议提供一个统一的调用接口，而不应该拆分成多个。

我们可以编写一个枚举类，来枚举所有的客户端类型。
app\libs\enums.py
```
from enum import Enum

# 定义一个枚举
class ClientTypeEnum(Enum):
    USER_EMAIL =  100
    USER_MOBILE = 101

    # 微信小程序
    USER_MINA = 200
    #微信公众号
    UESR_WX = 201

```
1.构建client验证器
app\validators\forms.py
```
from wtforms import Form, StringField, IntegerField    # 字符串类型,数字类型
from wtforms.validators import DataRequired, length
from app.libs.enums import ClientTypeEnum

# 构建client验证器
class ClientForm(Form):
    account = StringField(validators=[DataRequired(), length(min=1, max=32)])
    secret = StringField()   # 由于客户端类型的不同，密码不一定要传入
    type = IntegerField(validators=[DataRequired()])

    # 验证client_type
    def validate_type(self, value):
        try:
        # 将用户传来的参数去枚举类中匹配，如果匹配失败，则抛出异常
        # 如果匹配成功则将int转换成枚举
            client = ClientTypeEnum(value.data)  # value.data 取到值
        except ValueError as e:
            raise e

```
2.处理不同客户端注册的方案
由于python没有switch-case，我们可以使用dict来替换
app\api\v1\client.py
```
from app.libs.redprint import Redprint

from app.validators.forms import ClientForm
from flask import request
from app.libs.enums import ClientTypeEnum

api = Redprint('client')  # 实例化一个Redprint

@api.route('/register', methods = ['PSOT'] )  # 路由注册
def create_client():
    # 表单 - 一般网页  json - 一般移动端
    # 注册 登录
    # 参数 校验  接收参数
    # WTForms 验证表单

#用来接收json类型的参数
    data = request.json
# 关键字参数data是wtform中用来接收json参数的方法
    form = ClientForm(data=data)

    if form.validate():
# 替代switchcase-{Enum_name:handle_func}
        promise = {
            ClientTypeEnum.USER_EMAIL: __register_user_by_email#,
            # ClientTypeEnum.USER_MINA: __register_user_by_MINA   # 可在此处构建多种枚举类型
        }

def __register_user_by_email():
    pass

# def __register_user_by_MINA():
#     pass
```
3.用户模型的设计
app\models\base.py

```
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy, BaseQuery
from sqlalchemy import Column, Integer, SmallInteger
from contextlib import contextmanager


class SQLAlchemy(_SQLAlchemy):
    @contextmanager
    def auto_commit(self):
        try:
            yield
            self.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e


class Query(BaseQuery):
    def filter_by(self, **kwargs):
        if 'status' not in kwargs.keys():
            kwargs['status'] = 1
        return super(Query, self).filter_by(**kwargs)


db = SQLAlchemy(query_class=Query)


class Base(db.Model):
    __abstract__ = True
    create_time = Column(Integer)
    status = Column(SmallInteger, default=1)

    def __init__(self):
        self.create_time = int(datetime.now().timestamp())

    @property
    def create_datetime(self):
        if self.create_time:
            return datetime.fromtimestamp(self.create_time)
        else:
            return None

    def set_attrs(self, attrs_dict):
        for key, value in attrs_dict.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)

    def delete(self):
        self.status = 0

```
app\models\user.py

```
from sqlalchemy import inspect, Column, Integer, String, SmallInteger, orm
from werkzeug.security import generate_password_hash, check_password_hash

# from app.libs.error_code import NotFound, AuthFailed
from app.models.base import Base
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
```
添加一个注册的方法
```

from sqlalchemy import inspect, Column, Integer, String, SmallInteger, orm
from werkzeug.security import generate_password_hash, check_password_hash

# from app.libs.error_code import NotFound, AuthFailed
from app.models.base import Base , db
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
```
插件的注册
app\__init__.py
```

from flask import Flask


# 将Blueprint注册到flask核心对象上,并传入一个前缀'/v1'
def register_blueprints(app):
    # from app.api.v1.user import user
    # from app.api.v1.book import book
    # app.register_blueprint(user)
    # app.register_blueprint(book)
    from app.api.v1 import create_blueprint_v1
    app.register_blueprint(create_blueprint_v1(), url_prefix = '/v1')

def registe_plugin(app):  # 插件的注册
    from app.models.base import db
    db.init_app(app)

    with app.app_context():  # 上下文环境 把app推入到上下文栈中 才能使用create_all
        db.create_all()  # 来创建所有数据库，数据表

def create_app():
    app = Flask(__name__)   # 实例化flask核心对象
    app.config.from_object('app.config.secure')  # 读取配置文件下的secure
    app.config.from_object('app.config.setting') # 读取配置文件下的setting

    register_blueprints(app)    # 注册蓝图到核心对象上
    registe_plugin(app)  # 最后调用 registe_plugin

    return app
    
    
```

4.完成客户端注册
之前我们的ClientForm并没有nickname，但是注册email用户的时候是需要的，所以我们建立一个UserEmailForm继承ClientForm完成他自己的业务
不能从request.json 中拿，因为这个参数没经过校验
```

from wtforms import Form, StringField, IntegerField ,ValidationError    # 字符串类型,数字类型,异常
from wtforms.validators import DataRequired, length,  Email, Regexp
from app.libs.enums import ClientTypeEnum
from app.models.user import User

# 构建client验证器
class ClientForm(Form):
    account = StringField(validators=[DataRequired(), length(min=1, max=32)])
    secret = StringField()   # 由于客户端类型的不同，密码不一定要传入
    type = IntegerField(validators=[DataRequired()])

    # 验证client_type
    def validate_type(self, value):
        try:
        # 将用户传来的参数去枚举类中匹配，如果匹配失败，则抛出异常
        # 如果匹配成功则将int转换成枚举
            client = ClientTypeEnum(value.data)  # value.data 取到值
        except ValueError as e:
            raise e
    # 面向对象的继承特性，减少代码量，ClientForm是很有必要存在的
        self.type = client  # 将枚举赋值给 type

class UserEmailForm(ClientForm):
    account = StringField(validators=[
        Email(message='validate email')
        ])  # 必须是Email
    secret = StringField(validators=[
        DataRequired(),
        Regexp(r'^[A-Za-z0-9_*&$#@]{6,22}$')
        ]) #必须要密码，密码格式 
    nickname = StringField(validators=[DataRequired(),
                                       length(min=2, max=22)])  # 新增一个个性化参数nickname

    def validate_account(self, value):   # 验证账号是否已经注册
        if User.query.filter_by(email=value.data).first():  # 如果能查询到email
            raise ValidationError()   # 则抛出异常
```
完成视图函数的编写
```

from app.libs.redprint import Redprint

from app.validators.forms import ClientForm,UserEmailForm
from flask import request
from app.libs.enums import ClientTypeEnum
from app.models.user import User

api = Redprint('client')  # 实例化一个Redprint

@api.route('/register', methods = ['POST'] )  # 路由注册  # 因为这里把POST打成PSOT，导致不能使用POST访问，状态码405
def create_client():                         
    # 表单 - 一般网页  json - 一般移动端
    # 注册 登录
    # 参数 校验  接收参数
    # WTForms 验证表单

#用来接收json类型的参数
    data = request.json
# 关键字参数data是wtform中用来接收json参数的方法
    form = ClientForm(data = data)  # data =   来接收json

    if form.validate():
# 替代switchcase-{Enum_name:handle_func}
        promise = {
            ClientTypeEnum.USER_EMAIL: __register_user_by_email#,
            # ClientTypeEnum.USER_MINA: __register_user_by_MINA   # 可在此处构建多种枚举类型
        }
        promise[form.type.data]()
    return 'sucess'  #  暂时返回sucess
#总 ↑

#分 ↓

def __register_user_by_email():
    form = UserEmailForm(data=request.json)
    if form.validate():
        User.register_by_email(form.nickname.data,
                               form.account.data,
                               form.secret.data)


# def __register_user_by_MINA():
#     pass

```
create_client和__register_user_by_email是一个总-分的关系，客户端注册的种类是比较多的，但是这些众多的种类又有一些共通的东西，比如处理客户端的type的值，就是所有的客户端都要携带的参数。对于这些共有的参数，我们就统一在create_client,ClientForm中进行处理
 对于不同的客户端的特色的属性和功能，我们放在“分”里面来，比如email的nikename

3.3 重构代码-自定义验证对象
我们之前写的代码，有一些细节问题。

1.传入错误的参数，虽然没有添加到数据库，但是返回 结果显示正常
这是因为，form.validate()如果校验不通过，他不会抛出异常，而是会将异常信息存储在form对象中。
 所以这个时候我们应该判断如果校验不通过，就抛出一个自定义的异常。
 
 **比如我之前在"type" = "100",错误，但还是会return sucess。**

werkzeug为我们提供的大量的异常，都继承自HTTPException，但是这些异常都很具体，不能为我们所用。不过我们可以自己定义一个异常来继承HTTPException

2.自定义异常
rest中状态码代表的意义
400 参数错误
401 未授权
403 禁止访问
404 没有找到资源或者页面
500 服务器未知错误
200 查询成功
201 更新/创建成功
204 删除成功
301/302 重定向

app\libs\erro_code.py
```
from werkzeug.exceptions import HTTPException
# 自定义异常类

class ClientTypeErro(HTTPException):
    code = 400
    description = (
        'client is invalid'
    )
```
修改后的试图函数
app\api\v1\client.py
```

from app.libs.redprint import Redprint

from app.validators.forms import ClientForm,UserEmailForm
from flask import request
from app.libs.enums import ClientTypeEnum
from app.models.user import User

# from werkzeug.exceptions import HTTPException   #  异常
from app.libs.erro_code import ClientTypeErro   # 导入自定义异常

api = Redprint('client')  # 实例化一个Redprint

@api.route('/register', methods = ['POST'] )  # 路由注册  # 因为这里把POST打成PSOT，导致不能使用POST访问，状态码405
def create_client():                         
    # 表单 - 一般网页  json - 一般移动端
    # 注册 登录
    # 参数 校验  接收参数
    # WTForms 验证表单

#用来接收json类型的参数
    data = request.json
# 关键字参数data是wtform中用来接收json参数的方法
    form = ClientForm(data = data)  # data =   来接收json

    if form.validate():
# 替代switchcase-{Enum_name:handle_func}
        promise = {
            ClientTypeEnum.USER_EMAIL: __register_user_by_email#,
            # ClientTypeEnum.USER_MINA: __register_user_by_MINA   # 可在此处构建多种枚举类型
        }
        promise[form.type.data]()
    else:
        raise ClientTypeErro()  # 抛出自定义异常
    return 'sucess'  #  暂时返回sucess
#总 ↑

#分 ↓

def __register_user_by_email():
    form = UserEmailForm(data=request.json)
    if form.validate():
        User.register_by_email(form.nickname.data,
                               form.account.data,
                               form.secret.data)


# def __register_user_by_MINA():
#     pass
```
修改完成之后，已经修复了之前的缺陷，但是这样爆出了两个问题：
 1.代码太啰嗦了，每个试图函数里，都需要这么写
 2.ClientTypeError只是代表客户端类型异常，其他的参数校验不通过也抛出这个异常的话不合适

2.异常返回的标准与重要性
我们的restapi返回的信息主要分为以下三类:
 1.页数数据信息
 2.操作成功提示信息
 3.错误异常信息

如果错误异常信息不够标准，那么客户端很难去处理我们的错误异常。

无论上面三种，都属于输出，REST-API要求输入输出都要返回JSON

3.自定义ApiException
通过分析HttpException的get_body,get_header源码我们可以知道，这两个方法分别组成了默认异常页面的header和html文本，所以如果要让我们的异常返回json格式的信息，需要继承HttpException并重写这两个方法.  **万不得已,不要动框架源代码**  
 HttpException 源代码部分
```
class HTTPException(Exception):

    """
    Baseclass for all HTTP exceptions.  This exception can be called as WSGI
    application to render a default error page or you can catch the subclasses
    of it independently and render nicer error messages.
    """

    code = None
    description = None

    def __init__(self, description=None, response=None):
        Exception.__init__(self)
        if description is not None:
            self.description = description
        self.response = response

    def get_body(self, environ=None):
        """Get the HTML body."""
        return text_type((
            u'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n'
            u'<title>%(code)s %(name)s</title>\n'
            u'<h1>%(name)s</h1>\n'
            u'%(description)s\n'
        ) % {
            'code':         self.code,
            'name':         escape(self.name),
            'description':  self.get_description(environ)
        })

    def get_headers(self, environ=None):
        """Get a list of headers."""
        return [('Content-Type', 'text/html')]
```
app\libs\erro.py
```

from werkzeug.exceptions import HTTPException
from flask import request,json

# 重写 HTTPException

class APIException(HTTPException):
    # 定义默认异常信息
    code = 500
    msg = 'sorry, we make a mistake'
    erro_code = 999     # 自定义的错误码   # 建议新建一个code.md记录自定义的错误码

    def __init__(self, msg = None, code = None, erro_code = None,
                headers = None):   # 给定None ,不传就是默认值

        # 传了的话，就是选传的值
        if code:
            self.code = code
        if erro_code:
            self.erro_code = erro_code
        if msg:
            self.msg = msg   
        super(APIException, self).__init__(self.msg, None)   # 继承

    def get_body(self, environ=None):
        body = dict(
            msg = self.msg,
            erro_code = self.erro_code,
            # request = 'POST v1/client/register'
            request = request.method+' '+self.get_url_no_param() 
        )       
        text = json.dumps(body)  # 将字典转换为json 文本  json 序列化
        return text

    def get_headers(self, environ=None):
        return [('Content-Type', 'application/json')]  # 将返回标识成json

    @staticmethod
    def get_url_no_param():  # 没有？后面的参数
        full_path = request.full_path  # 拿到 url完整路径
        main_path = full_path.split('?') # 去掉？和后面
        return main_path[0]


```
