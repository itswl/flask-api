from app import create_app
from app.libs.erro_code import ServerError
from app.libs.erro import APIException
from werkzeug.exceptions import HTTPException

app = create_app()

@app.errorhandler(Exception)  # python 基类的异常,因为我们要捕捉所有异常
def framework_error(e):
    if isinstance(e, APIException):
        return e
    if isinstance(e, HTTPException):  # 转化成APIException
        code = e.code
        msg = e.description
        error_code = 1007
        return APIException(msg, code, error_code)
    else:
        if not app.config['DEBUG']: # 判断是否在调试模式,不再,直接返回
            return ServerError()
        else:
            raise e 
        return ServerError()


if __name__ == '__main__':
    app.run(debug=True)


'''
（以删除master分支 .idea文件夹为例）
git rm -r --cached .idea  #--cached不会把本地的.idea删除
git commit -m 'delete .idea dir'
git push -u origin master


'''