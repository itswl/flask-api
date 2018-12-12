# 前言
### flask VS Django
可以理解为安装各种插件的 flask = Django



# 1.1 初始化项目

### 1.一个项目的初始化流程如下：



![image](http://upload-images.jianshu.io/upload_images/14597179-e18c55d1fb28effc?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240) 


### 2.新建入口文件

app/__init__.py
```
from flask import Flask

def create_app():
    app = Flask(__name__)   # 实例化flask核心对象
    app.config.from_object('app.config.secure')  # 读取配置文件下的secure
    app.config.from_object('app.config.setting') # 读取配置文件下的setting

    register_blueprints(app)    # 注册蓝图到核心对象上
    
    return app
```

ginger.py
```
from app import create_app

app = create_app()



if __name__ == '__main__':
    app.run(debug=True)
```

# 1.2 红图

### 1.蓝图拆分视图函数的缺陷的缺陷

1.蓝图的作用并不是用来拆分视图函数的，而是用来拆分模块的 2.使用蓝图，统一个业务模型的试图函数的前缀都一样，代码重复啰嗦

### 2.打开思维，创建自己的redprint-红图

为了解决上面的两个问题，我们可以模仿蓝图，构建一个自定义的对象-红图，红图的定位是用来拆分视图，也就是视图函数层

![image](http://upload-images.jianshu.io/upload_images/14597179-e0fda6bfede1225d?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240) 

我们采用自顶向下的编程思想，先编写redprint在试图函数中的使用代码，再编写redprint具体的实现

#### 2.1 视图函数向红图的注册

app/api/v1/book.py
```
from app.libs.redprint import Redprint


api = Redprint('book')   # 实例化一个Redprint

@api.route('/get')     # 使用Redprint 来注册视图函数
def get_book():
    return 'get_book'

@api.route('/create')
def create_book():
    return 'create_book'
```
app/api/v1/user.py
```
# 使用Blueprint注册视图函数
# from flask import Blueprint

# user = Blueprint('user',__name__)

# @user.route('/v1/user/get')
# def get_user():
#     return 'imwl'

from app.libs.redprint import Redprint

api = Redprint('user')

@api.route('/get')
def get_user():
    return 'get_user'

@api.route('/create')
def create_user():
    return 'create_user'
```
#### 2.2 红图向蓝图的注册

app/api/__init__.py
```
from flask import Blueprint
from app.api.v1 import user, book

 #  创建一个Bluerint,把Redprint注册到Blueprint上，并传入Redprint一个前缀'/book
def create_blueprint_v1():
    bp_v1 = Blueprint('v1', __name__) 
    
# 假设api有register的方法，后面再实现, url_prefix解决前缀问题
  #  book.api.register(bp_v1, url_prefix='/book')
  #  user.api.register(bp_v1, url_prefix='/user')  # 后文 有解释为什么不传 url_prefix  

    user.api.register(bp_v1) 
    book.api.register(bp_v1)  
    return bp_v1
from flask import Blueprint
from app.api.v1 import book, user


def create_blueprint_v1():
    bp_v1 = Blueprint('v1', __name__)

    book.api.register(bp_v1, url_prefix='/book')
    user.api.register(bp_v1, url_prefix='/user')
    return bp_v1
```
#### 2.3 蓝图向Flask核心对象的注册

app/app.py
```
from flask import Flask


# 将Blueprint注册到flask核心对象上,并传入一个前缀'/v1'
def register_blueprints(app):
    # from app.api.v1.user import user  #（这些是没改造前，用blueprint的注册方式）
    # from app.api.v1.book import book
    # app.register_blueprint(user)
    # app.register_blueprint(book)
    from app.api.v1 import create_blueprint_v1
    app.register_blueprint(create_blueprint_v1(), url_prefix = '/v1')

def create_app():
    app = Flask(__name__)   # 实例化flask核心对象
    app.config.from_object('app.config.secure')  # 读取配置文件下的secure ,app/config/secure.py
    app.config.from_object('app.config.setting') # 读取配置文件下的setting, app/config/setting.py

    register_blueprints(app)    # 注册蓝图到核心对象上
    
    return app
    
```
### 3.实现Redprint

因为我们的红图的作用就是要代替蓝图来实现试图函数的拆分，所以功能实现上可以参考蓝图的实现。

#### 3.1 装饰性route的实现

蓝图的实现
```
def route(self, rule, **options):
"""Like :meth:`Flask.route` but for a blueprint. The endpoint for the
:func:`url_for` function is prefixed with the name of the blueprint.
"""
def decorator(f):
# 获取endpoint，默认为试图函数名
endpoint = options.pop("endpoint", f.__name__)
# 注册视图函数
self.add_url_rule(rule, endpoint, f, **options)
return f
return decorator
```
红图的实现可以模仿蓝图的实现结构 ，由于红图的route里没有办法拿到蓝图的对象，所以我们可以先把他们存储起来，等碰到的时候再进行注册
```
class Redprint:
    def __init__(self,name):
        self.name = name 
        self.mound = []

    def route(self, rule, **options):
        def decorator(f):
            self.mound.append((f, rule, options))
            return f
        return decorator
```
#### 3.2 register方法

在register方法中可以获取到蓝图对象，所以之前route中视图函数的注册延迟到这里进行
```
# 红图的实现可以模仿蓝图的实现结构 ，
# 由于红图的route里没有办法拿到蓝图的对象，
# 所以我们可以先把他们存储起来，等碰到的时候再进行注册

class Redprint:
    def __init__(self,name):
        self.name = name 
        self.mound = []

    def route(self, rule, **options):
        def decorator(f):
            self.mound.append((f, rule, options))
            return f
        return decorator

    # 在register方法中可以获取到蓝图对象，
    # 所以之前route中视图函数的注册延迟到这里进行
    def register(self, bp,  url_prefix = None):
    # 如果不传url_prefix 则默认使用name
        if url_prefix is None:
            url_prefix = '/'+self.name   # 定义 Redprint 前缀
        # python的自动拆包
        for f, rule, options in self.mound:
            endpoint = options.pop("endpoint", f.__name__)
            # 将视图函数注册到蓝图上来
            bp.add_url_rule(url_prefix + rule, endpoint, f, **options)

```

## 流程梳理

1. 模仿Blueprint自定义Redprint
2. app/api/v1/book.py中实例化一个Redprint 来注册视图函数。
3. app/api/v1/__init__.py 中创建一个Bluerint,把Redprint注册到Blueprint上，并传入Redprint一个前缀,如: '/book'
4. 在app/__init__.py 中 将Blueprint注册到flask核心对象上,并传入一个前缀，如： '/v1'
