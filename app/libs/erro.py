

from werkzeug.exceptions import HTTPException
from flask import request,json

# 重写 HTTPException

class APIException(HTTPException):
    # 定义默认异常信息
    code = 500
    msg = 'sorry, we make a mistake'
    erro_code = 999     # 自定义的错误码   # 建议新建一个code.md记录自定义的错误码

    def __init__(self, msg = None, code = None, erro_code = None,
                headers = None):   # 给定None ,不传就是默认值

        # 传了的话，就是选传的值
        if code:
            self.code = code
        if erro_code:
            self.erro_code = erro_code
        if msg:
            self.msg = msg   
        super(APIException, self).__init__(self.msg, None)   # 继承

    def get_body(self, environ=None):
        body = dict(
            msg = self.msg,
            erro_code = self.erro_code,
            # request = 'POST v1/client/register'
            request = request.method+' '+self.get_url_no_param() 
        )       
        text = json.dumps(body)  # 将字典转换为json 文本  json 序列化
        return text

    def get_headers(self, environ=None):
        return [('Content-Type', 'application/json')]  # 将返回标识成json

    @staticmethod
    def get_url_no_param():  # 没有？后面的参数
        full_path = request.full_path  # 拿到 url完整路径
        main_path = full_path.split('?') # 去掉？和后面
        return main_path[0]

