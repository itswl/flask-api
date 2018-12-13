# 4.1 重写WTForms

### 优化1

之前的代码，修改完成之后，已经修复了之前的缺陷，但是这样爆出了两个问题： 1.代码太啰嗦了，每个试图函数里，都需要这么写 2.ClientTypeError只是代表客户端类型异常，其他的参数校验不通过也抛出这个异常的话不合适

为了解决上面的问题，我们需要重写wtforms

## 思路
  继承原有的wtforms,重写validate_for_api，**修改wtforms为抛出异常**
定义一个自定义BaseForm，让其他的Form来继承
app\validators\base.py
```
from wtforms import Form
from app.libs.erro_code import ParameterException

class BaseForm(Form):
    def __init__(self, data):
        super(BaseForm, self).__init__(data=data)   # 调用父类构造函数

    def validate_for_api(self):
        valid = super(BaseForm, self).validate()  # 调用父类的构造方法 # 验证是否通过
        if not valid:   # 没通过
            # 所有异常类信息在form errors 中 
            raise ParameterException(msg=self.errors) #  抛出异常  # 公共的自定义异常类
```
定义公共异常类

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
```

以后我们的试图函数就可以这样编写
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
   
    form.validate_for_api()
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

### 优化2

目前我们每次都需要从request中取出json信息再传入到Form对象中，优化的思路是，直接传入request，在BaseForm中取出json
app\validators\base.py
```
from wtforms import Form
from app.libs.erro_code import ParameterException
from flask import request

class BaseForm(Form):
    # def __init__(self, data):
    def __init__(self):
        data = request.json
        super(BaseForm, self).__init__(data=data)   # 调用父类构造函数

    def validate_for_api(self):
        valid = super(BaseForm, self).validate()  # 调用父类的构造方法 # 验证是否通过
        if not valid:   # 没通过
            # 所有异常类信息在form errors 中 
            raise ParameterException(msg=self.errors) #  抛出异常  # 公共的自定义异常类
```


### 优化3

每次都需要实例化Form对象，再调用validate_for_api()方法，我们可以让validate_for_api方法返回一个self对象，这样就只需要一行代码就可以解决了
app\validators\base.py
```
from wtforms import Form
from app.libs.erro_code import ParameterException
from flask import request

class BaseForm(Form):
    # def __init__(self, data):
    def __init__(self):
        data = request.json
        super(BaseForm, self).__init__(data=data)   # 调用父类构造函数

    def validate_for_api(self):
        valid = super(BaseForm, self).validate()  # 调用父类的构造方法 # 验证是否通过
        if not valid:   # 没通过
            # 所有异常类信息在form errors 中 
            raise ParameterException(msg=self.errors) #  抛出异常  # 公共的自定义异常类
        return self
```
### 优化4

操作成功也需要返回json结构，且结构应该和异常的时候一样，所以我们可以定义一个Success继承APIException
app\libs\erro_code.py
```

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
```
优化后视图函数
app\api\v1\client.py
```

from app.libs.redprint import Redprint

from app.validators.forms import ClientForm,UserEmailForm
# from flask import request  #  转移到Baseform中去了
from app.libs.enums import ClientTypeEnum
from app.models.user import User


# from werkzeug.exceptions import HTTPException   #  异常
from app.libs.erro_code import ClientTypeErro, ParameterException ,Success    # 导入自定义异常

api = Redprint('client')  # 实例化一个Redprint

@api.route('/register', methods = ['POST'] )  # 路由注册  # 因为这里把POST打成PSOT，导致不能使用POST访问，状态码405
def create_client():                         
    # 表单 - 一般网页  json - 一般移动端
    # 注册 登录
    # 参数 校验  接收参数
    # WTForms 验证表单

#用来接收json类型的参数
    # data = request.json
# 关键字参数data是wtform中用来接收json参数的方法
    # form = ClientForm(data = data)  # data =   来接收json
    # form = ClientForm()   # 转移到 BaseForm 中

    # form.validate_for_api()
    form = ClientForm().validate_for_api()
# 替代switchcase-{Enum_name:handle_func}
    promise = {
            ClientTypeEnum.USER_EMAIL: __register_user_by_email#,
            # ClientTypeEnum.USER_MINA: __register_user_by_MINA   # 可在此处构建多种枚举类型
        }
    promise[form.type.data]()

    return Success()  #  将成功返回也当作一中 APIException
#总 ↑

#分 ↓

def __register_user_by_email():
#     form = UserEmailForm()
# # if form.validate():
#     form.validate_for_api() 
    form = UserEmailForm().validate_for_api()   # 为什么有括号
    User.register_by_email(form.nickname.data,
                               form.account.data,
                               form.secret.data)


# def __register_user_by_MINA():
#     pass
```
我们可以接受定义时候的复杂，但是不能够接受调用的时候复杂

定义是一次性的，但是调用是多次的，如果调用太过于复杂，会使得我们的 代码太过于臃肿

# 4.2 全局异常处理

当系统抛出不是我们自己定义的APIException的时候，返回的结果仍然会变成一个HTML文本。

我们在写代码的过程中，有那么类型的异常： 1.已知异常：我们可以预知的。如枚举转换的时候抛出的异常，这时候我们就会提前使用try-except进行处理。也可以抛出APIException 2.未知异常：完全没有预料到的。会由框架抛出的内置异常

我们可以使用flask给我们提供的处理全局异常的装饰器，采用AOP的设计思想，捕捉所有类型的异常。
```
from app import create_app
from app.libs.erro_code import ServerError
from app.libs.erro import APIException
from werkzeug.exceptions import HTTPException

app = create_app()

@app.errorhandler(Exception)  # python 基类的异常,因为我们要捕捉所有异常
def framework_error(e):
    if isinstance(e, APIException):
        return e
    if isinstance(e, HTTPException):  # 转化成APIException
        code = e.code
        msg = e.description
        error_code = 1007
        return APIException(msg, code, error_code)
    else:
        if not app.config['DEBUG']: # 判断是否在调试模式,不再,直接返回
            return ServerError()
        else:
            raise e 
        return ServerError()


if __name__ == '__main__':
    app.run(debug=True)

```
