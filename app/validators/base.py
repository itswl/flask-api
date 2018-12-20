
'''
1.代码太啰嗦了，每个试图函数里，都需要这么写

2.ClientTypeError只是代表客户端类型异常，其他的参数校验不通过也抛出这个异常的话不合适

为了解决上面的问题，我们需要重写wtforms

定义一个自定义BaseForm，让其他的Form来继承
'''
from wtforms import Form
from app.libs.erro_code import ParameterException
from flask import request

class BaseForm(Form):
    # def __init__(self, data):
    def __init__(self):
        # data = request.json  # 获取json数据格式
        data = request.get_json(silent = True)  #  出现错误，不报异常
        args = request.args.to_dict()  # 完成查询参数的获取
        super(BaseForm, self).__init__(data=data,**args)   # 调用父类构造函数

    def validate_for_api(self):
        valid = super(BaseForm, self).validate()  # 调用父类的构造方法 # 验证是否通过
        if not valid:   # 没通过
            # 所有异常类信息在form errors 中 
            raise ParameterException(msg=self.errors) #  抛出异常  # 公共的自定义异常类
        return self

