


from app import create_app
from app.models.base import db
from app.models.user import User

app = create_app()
with app.app_context():
    with db.auto_commit():
        # 离线脚本，创建一个超级管理员
        user = User()
        user.nickname = 'Super'
        user.password = '123456'
        user.email = '999@qq.com'
        user.auth = 2
        db.session.add(user)

with app.app_context():
    for v in range(1, 100):
        with db.auto_commit():
        # 离线脚本，批量创建普通用户
            user = User()
            user.nickname = 'user'+str(v)
            user.password = '123456'
            user.email = 'user'+str(v)+'@qq.com'
            user.auth = 1
            db.session.add(user)

# 直接运行就能创建