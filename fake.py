
#  离线脚本

from app import create_app
from app.models.base import db
from app.models.user import User

app = create_app()


with app.app_context():
    with db.auto_commit():
        # 创建一个超级管理员
        user = User()
        user.nickname = 'Super'
        user.password = '123456'
        user.email = '999@qq.com'
        user.auth = 2
        db.session.add(user)

with app.app_context():
    for v in range(1, 100):
        with db.auto_commit():
        # 批量创建普通用户
            user = User()
            user.nickname = 'user'+str(v)
            user.password = '123456'
            user.email = 'user'+str(v)+'@qq.com'
            user.auth = 1
            db.session.add(user)


with app.app_context():
    for v in range(2, 101):  # 得先查看id
        with db.auto_commit():
        # 批量软删除用户
            id = int(v)
            user = User.query.filter_by(id=id).first_or_404()
            user.delete() # base中有定义delete,将status改为0
            db.session.add(user)

with app.app_context():
    for v in range(2, 101):
        with db.auto_commit():
        # 批量删除用户
            id = int(v)
            user = User.query.get(id)  # 因为filiter_by有改写，不能查到status=0
            db.session.delete(user)