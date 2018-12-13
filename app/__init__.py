
from flask import Flask


# 将Blueprint注册到flask核心对象上,并传入一个前缀'/v1'
def register_blueprints(app):
    # from app.api.v1.user import user
    # from app.api.v1.book import book
    # app.register_blueprint(user)
    # app.register_blueprint(book)
    from app.api.v1 import create_blueprint_v1
    app.register_blueprint(create_blueprint_v1(), url_prefix = '/v1')

def create_app():
    app = Flask(__name__)   # 实例化flask核心对象
    app.config.from_object('app.config.secure')  # 读取配置文件下的secure
    app.config.from_object('app.config.setting') # 读取配置文件下的setting

    register_blueprints(app)    # 注册蓝图到核心对象上
    
    return app
    
    
    
    


