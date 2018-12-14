

# from flask.json import JSONEncoder as _JSONEncoder

# from app.libs.erro_code import ServerError
# from datetime import date

# class JSONEncoder(_JSONEncoder):
# 	def default(self,o):
# 		# return o.__dict__  # 内置方法，将对象转化为字典  # 缺点是只能转换实例变量，不能将类变量也转换成字典
# 		# return dict(o) # 考虑不全面.o得有上次定义的那两种方法才不会报错

# 		if hasattr(o, 'keys') and hasattr(o, '__getitem__'):
# 			return dict(o)   # 得有这两种方法 才会return dict(o)
# 		if isinstance(o, date):  # 如果是 时间类型
# 			return o.strftime('%Y-%m-%d')
# 		raise ServerError()
# '''
# 问题：Python文件运行时报TabError: inconsistent use of tabs and spaces in indentation

# 原因：说明Python文件中混有Tab和Space用作格式缩进。这通常是使用外部编辑器编辑Python文件时，自动采用Tab进行格式缩进。
# 拷贝出错
# '''


# class Flask(_Flask):  # 定义自己的Flask核心对象，继承原来的Flask核心对象
# 	json_encoder = JSONEncoder # 替换原本的JSONEncoder

# 之前编写的新的Flask类，JsonEncoder类都是不会轻易改变的，放到app.py中
# 一些其他方法，却是 经常改变的，应该把他们放在init文件中

from .app import Flask
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
    
    
    
    


