# 4.1 重写WTForms

### 优化1

之前的代码，修改完成之后，已经修复了之前的缺陷，但是这样爆出了两个问题： 1.代码太啰嗦了，每个试图函数里，都需要这么写 2.ClientTypeError只是代表客户端类型异常，其他的参数校验不通过也抛出这个异常的话不合适

为了解决上面的问题，我们需要重写wtforms

定义一个自定义BaseForm，让其他的Form来继承
```
class BaseForm(Form):
def __init__(self, data):
super(BaseForm, self).__init__(data=data)

def validate_for_api(self):
valid = super(BaseForm, self).validate()
if not valid:
raise ParameterException(msg=self.errors)
```
以后我们的试图函数就可以这样编写
```
@api.route('/register', methods=['POST'])
def create_client():
data = request.json
form = ClientForm(data=data)

form.validate_for_api()
promise = {
ClientTypeEnum.USER_EMAIL: __register_user_by_email
}
promise[form.type.data]()

return 'success'
```
### 优化2

目前我们每次都需要从request中取出json信息再传入到Form对象中，优化的思路是，直接传入request，在BaseForm中取出json

### 优化3

每次都需要实例化Form对象，再调用validate_for_api()方法，我们可以让validate_for_api方法返回一个self对象，这样就只需要一行代码就可以解决了
```
class BaseForm(Form):
def __init__(self, request):
# 优化2
data = request.json
super(BaseForm, self).__init__(data=data)

def validate_for_api(self):
valid = super(BaseForm, self).validate()
if not valid:
raise ParameterException(msg=self.errors)
# 优化3
return self
```
### 优化4

操作成功也需要返回json结构，且结构应该和异常的时候一样，所以我们可以定义一个Success继承APIException
```
class Success(APIException):
code = 201
msg = 'ok'
error_code = 0
```
视图函数
```
@api.route('/register', methods=['POST'])
def create_client():
form = ClientForm(request).validate_for_api()
promise = {
ClientTypeEnum.USER_EMAIL: __register_user_by_email
}
promise[form.type.data]()

return Success()
```
我们可以接受定义时候的复杂，但是不能够接受调用的时候复杂

定义是一次性的，但是调用是多次的，如果调用太过于复杂，会使得我们的 代码太过于臃肿

# 4.2 全局异常处理

当系统抛出不是我们自己定义的APIException的时候，返回的结果仍然会变成一个HTML文本。

我们在写代码的过程中，有那么类型的异常： 1.已知异常：我们可以预知的。如枚举转换的时候抛出的异常，这时候我们就会提前使用try-except进行处理。也可以抛出APIException 2.未知异常：完全没有预料到的。会由框架抛出的内置异常

我们可以使用flask给我们提供的处理全局异常的装饰器，采用AOP的设计思想，捕捉所有类型的异常。
```
@app.errorhandler(Exception)
def framework_error(e):
if isinstance(e, APIException):
return e
if isinstance(e, HTTPException):
code = e.code
msg = e.description
error_code = 1007
return APIException(msg, code, error_code)
else:
# TODO log
if not app.config['DEBUG']:
return ServerError()
else:
raise e
```
