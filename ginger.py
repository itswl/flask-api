from flask import request
from werkzeug.exceptions import HTTPException
from app import create_app
from app.libs.erro import APIException
from app.libs.erro_code import ServerError

app=create_app()
# 定义全局异常处理
@app.errorhandler(Exception)
def framework_error(e):
    bluename=request.blueprint
    # 如果是API模块的异常
    if bluename=='v1':
        # 可预见的自定义异常
        if isinstance(e,APIException):
            return e
        # 不可预见的HTTPP异常
        if isinstance(e,HTTPException):
            code=e.code
            msg=e.description
            error_code=1007
            return APIException(code,error_code,msg)
        # 不可预见的非正常异常
        else:
            if app.config['DEBUG']:
                raise e
            else:
                return ServerError()
    # 如果是web模块的异常
    elif bluename == 'web':
        pass
if __name__=='__main__':
    app.run(debug=False)


'''
（以删除master分支 .idea文件夹为例）
git rm -r --cached .idea  #--cached不会把本地的.idea删除
git commit -m 'delete .idea dir'
git push -u origin master


'''