
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
    
    
    
    


