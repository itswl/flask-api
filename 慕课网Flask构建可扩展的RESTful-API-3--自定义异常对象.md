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

1.构建client验证器
```
class ClientForm(Form):
account = StringField(validators=[DataRequired(), length(
min=1, max=32
)])
secret = StringField()
type = IntegerField(validators=[DataRequired()])

# 验证client_type
def validate_type(self, value):
try:
# 将用户传来的参数去枚举类中匹配，如果匹配失败，则抛出异常
# 如果匹配成功则将int转换成枚举
client = ClientTypeEnum(value.data)
except ValueError as e:
raise e
```
2.处理不同客户端注册的方案
由于python没有switch-case，我们可以使用dict来替换
```
@api.route('/register')
def create_client():
# request.json
用来接收json类型的参数
data = request.json
# 关键字参数data是wtform中用来接收json参数的方法
form = ClientForm(data=data)

if form.validate():
# 替代switchcase-{Enum_name:handle_func}
promise = {
ClientTypeEnum.USER_EMAIL: __register_user_by_email
}
```
3.用户模型的设计
```
class User(Base):
id = Column(Integer, primary_key=True)
email = Column(String(50), unique=True, nullable=False)
auth = Column(SmallInteger, default=1)
nickname = Column(String(24), nullable=False)
_password = Column('password', String(128))

@property
def password(self):
return self._password

@password.setter
def password(self, raw):
self._password = generate_password_hash(raw)

# 从面向对象的角度考虑，在一个对象中创建一个对象本身这个是不合理的。
# 但是如果将他声明为一个静态方法，那么就是合理的
@staticmethod
def register_by_email(nikename, account, secert):
with db.auto_commit():
user = User()
user.nickname = nikename
user.email = account
user.password = secert
db.session.add(user)
```
4.完成客户端注册
之前我们的ClientForm并没有nickname，但是注册email用户的时候是需要的，所以我们建立一个UserEmailForm继承ClientForm完成他自己的业务
```
class UserEmailForm(ClientForm):
account = StringField(validators=[
Email(message='validate email')
])
secret = StringField(validators=[
DataRequired(),
Regexp(r'^[A-Za-z0-9_*&$#@]{6,22}$')
])
nickname = StringField(validators=[DataRequired(),
length(min=2, max=22)])

def validate_account(self, value):
if User.query.filter_by(email=value.data).first():
raise ValidationError()
```
完成视图函数的编写
```
@api.route('/register')
def create_client():
data = request.json
form = ClientForm(data=data)

if form.validate():
promise = {
ClientTypeEnum.USER_EMAIL: __register_user_by_email
}
promise[form.type.data]()
pass


def __register_user_by_email():
form = UserEmailForm(data=request.json)
if form.validate():
User.register_by_email(form.nickname.data,
form.account.data,
form.secret.data)
```
create_client和__register_user_by_email是一个总-分的关系，客户端注册的种类是比较多的，但是这些众多的种类又有一些共通的东西，比如处理客户端的type的值，就是所有的客户端都要携带的参数。对于这些共有的参数，我们就统一在create_client,ClientForm中进行处理
 对于不同的客户端的特色的属性和功能，我们放在“分”里面来，比如email的nikename

3.3 重构代码-自定义验证对象
我们之前写的代码，有一些细节问题。

1.传入错误的参数，虽然没有添加到数据库，但是返回 结果显示正常
这是因为，form.validate()如果校验不通过，他不会抛出异常，而是会将异常信息存储在form对象中。
 所以这个时候我们应该判断如果校验不通过，就抛出一个自定义的异常。

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
```
class ClientTypeError(HTTPException):
code = 400

description = (
'client is invalid'
)
```
修改后的试图函数
```
@api.route('/register', methods=['POST'])
def create_client():
data = request.json
form = ClientForm(data=data)

if form.validate():
promise = {
ClientTypeEnum.USER_EMAIL: __register_user_by_email
}
promise[form.type.data]()
else:
raise ClientTypeError()
return 'success'
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
通过分析HttpException的get_body,get_header源码我们可以知道，这两个方法分别组成了默认异常页面的header和html文本，所以如果要让我们的异常返回json格式的信息，需要继承HttpException并重写这两个方法
 HttpException
```
class HTTPException(Exception):

"""
Baseclass for all HTTP exceptions. This exception can be called as WSGI
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
'code': self.code,
'name': escape(self.name),
'description': self.get_description(environ)
})

def get_headers(self, environ=None):
"""Get a list of headers."""
return [('Content-Type', 'text/html')]
```
APIException
```
class APIException(HTTPException):
code = 500
error_code = 999
msg = 'sorry, we make a mistake'

def __init__(self, msg=None, code=None, error_code=None,
headers=None):
if code:
self.code = code
if error_code:
self.error_code = error_code
if msg:
self.msg = msg
super(APIException, self).__init__(self.msg, None)

def get_body(self, environ=None):
body = dict(
msg=self.msg,
error_code=self.error_code,
request=request.method+' '+self.get_url_no_param()
)
text = json.dumps(body)
return text

def get_headers(self, environ=None):
return [('Content-Type', 'application/json')]

@staticmethod
def get_url_no_param():
full_path = request.full_path
main_path = full_path.split('?')
return main_path[0]
```
