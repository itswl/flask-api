from flask import Flask


def register_blueprints(app):
    from app.api.v1.user import user
    from app.api.v1.book import book
    app.register_blueprint(user)   # 别弄成register_blueprints 了
    app.register_blueprint(book)
    

def creat_app():
    app = Flask(__name__)

    app.config.from_object('app.config.secure')  # 读取配置文件下的secure
    app.config.from_object('app.config.setting')

    register_blueprints(app)

    return app
