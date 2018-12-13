
from app.libs.redprint import Redprint

from app.validators.forms import ClientForm,UserEmailForm
from flask import request
from app.libs.enums import ClientTypeEnum
from app.models.user import User

# from werkzeug.exceptions import HTTPException   #  异常
from app.libs.erro_code import ClientTypeErro   # 导入自定义异常

api = Redprint('client')  # 实例化一个Redprint

@api.route('/register', methods = ['POST'] )  # 路由注册  # 因为这里把POST打成PSOT，导致不能使用POST访问，状态码405
def create_client():                         
    # 表单 - 一般网页  json - 一般移动端
    # 注册 登录
    # 参数 校验  接收参数
    # WTForms 验证表单

#用来接收json类型的参数
    data = request.json
# 关键字参数data是wtform中用来接收json参数的方法
    form = ClientForm(data = data)  # data =   来接收json

    if form.validate():
# 替代switchcase-{Enum_name:handle_func}
        promise = {
            ClientTypeEnum.USER_EMAIL: __register_user_by_email#,
            # ClientTypeEnum.USER_MINA: __register_user_by_MINA   # 可在此处构建多种枚举类型
        }
        promise[form.type.data]()
    else:
        raise ClientTypeErro()  # 抛出自定义异常
    return 'sucess'  #  暂时返回sucess
#总 ↑

#分 ↓

def __register_user_by_email():
    form = UserEmailForm(data=request.json)
    if form.validate():
        User.register_by_email(form.nickname.data,
                               form.account.data,
                               form.secret.data)


# def __register_user_by_MINA():
#     pass