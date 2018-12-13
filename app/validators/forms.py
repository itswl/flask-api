

from wtforms import  StringField, IntegerField ,ValidationError    # 字符串类型,数字类型,异常
from wtforms.validators import DataRequired, length,  Email, Regexp
from app.libs.enums import ClientTypeEnum
from app.models.user import User
from app.validators.base import BaseForm as Form # 改继承BaseForm

# 构建client验证器
class ClientForm(Form):  
    account = StringField(validators=[DataRequired(), length(min=1, max=32)])
    secret = StringField()   # 由于客户端类型的不同，密码不一定要传入
    type = IntegerField(validators=[DataRequired()])

    # 验证client_type
    def validate_type(self, value):
        try:
        # 将用户传来的参数去枚举类中匹配，如果匹配失败，则抛出异常
        # 如果匹配成功则将int转换成枚举
            client = ClientTypeEnum(value.data)  # value.data 取到值
        except ValueError as e:
            raise e
    # 面向对象的继承特性，减少代码量，ClientForm是很有必要存在的
        self.type.data = client  # 将枚举赋值给 type.data

class UserEmailForm(ClientForm):
    account = StringField(validators=[
        Email(message='validate email')
        ])  # 必须是Email
    secret = StringField(validators=[
        DataRequired(),
        Regexp(r'^[A-Za-z0-9_*&$#@]{6,22}$')
        ]) #必须要密码，密码格式 
    nickname = StringField(validators=[DataRequired(),
                                       length(min=2, max=22)])  # 新增一个个性化参数nickname

    def validate_account(self, value):   # 验证账号是否已经注册
        if User.query.filter_by(email=value.data).first():  # 如果能查询到email
            raise ValidationError()   # 则抛出异常