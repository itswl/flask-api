
from sqlalchemy import inspect, Column, Integer, String, SmallInteger, orm
from werkzeug.security import generate_password_hash, check_password_hash

from app.libs.erro_code import NotFound, AuthFailed
from app.models.base import Base , db ,MixinJSONSerializer
import datetime


class User(Base):
    id = Column(Integer, primary_key=True)
    email = Column(String(24), unique=True, nullable=False)
    nickname = Column(String(24), unique=True)
    auth = Column(SmallInteger, default=1)   # 做层级的标志
    _password = Column('password', String(100))

    def keys(self):
        return ['id', 'email', 'nickname', 'auth']

    # def __getitem__(self,item):  # 提取到公共类中 base 
    #     return getattr(self,item) 

    @property               
    def password(self):
        return self._password   #  对密码的处理

    @password.setter
    def password(self, raw):
        self._password = generate_password_hash(raw)    #  对密码的处理

    @staticmethod
    def register_by_email(nickname, account, secret):
        with db.auto_commit():
            user = User()
            user.nickname = nickname
            user.email = account
            user.password = secret
            db.session.add(user)

    @staticmethod
    def verify(email, password):
        user = User.query.filter_by(email=email).first_or_404()   # 查询出当前用户
        if not user.check_password(password):  # 检验密码
            raise AuthFailed()   #抛出异常
        scope = 'AdminScope' if user.auth == 2 else 'UserScope'  # 判断用户作用域，假设只有两个作用域
        return {'uid': user.id,'scope': scope}  #成功，返回uid   # 返回scope

    def check_password(self, raw):   # 密码检验
        if not self._password:
            return False
        return check_password_hash(self._password, raw)

    # def _set_fields(self):
    #     # self._exclude = ['_password']
    #     self._fields = ['_password', 'nickname']
