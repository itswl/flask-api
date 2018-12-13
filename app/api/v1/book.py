## 使用蓝图
# from flask import Blueprint

# book = Blueprint('book',__name__)

# @book.route('/v1/book/get')
# def get_book():
#     return 'hello world'



from app.libs.redprint import Redprint


api = Redprint('book')   # 实例化一个Redprint


@api.route('',methods = ['GET'])  # 使用Redprint 来注册视图函数
def get_book():
    return 'get_book'

@api.route('',methods = ['PUT'])
def update_book():
    return 'update_book'

@api.route('',methods = ['DELETE'])
def delete_book():
    return 'delete_book'

@api.route('',methods = ['POST'])
def create_book():
    return 'create_book'