
# from flask import Blueprint

# user = Blueprint('user',__name__)

# @user.route('/v1/user/get')
# def get_user():
#     return 'imwl'

from app.libs.redprint import Redprint
from app.libs.token_auth import auth
from app.models.user import User
from app.models.base import db
from flask import jsonify

api = Redprint('user')

# class Wei():
#     name = 'weilai'
#     age = 'age'

#     def __init__(self):
#         self.gender = 'male'

#     def keys(self):   
#         return ('name','age','gender')  #  取到 key ,  做到自定义key 
#         # # return ('name',)  # 一个元素的元组
#         # return ['name']  # return 序列类型的都可以

#     def __getitem__(self,item):  
#         return getattr(self,item)   # 取到 key对应的value

#@api.route('/get')  URL中不应该包含动词
@api.route('/<int:uid>', methods = ['GET'])  # 获取到用户的uid
@auth.login_required
def get_user(uid):   # 接收 uid
    user = User.query.get_or_404 (uid) # 获取到用户，用get_or_404简化判断用户是否存在
                                # 因为get_or_404 抛出的不是APIException,所以要重写
                                # query 属性下的方法 
    # r = {
    #     'nickname':user.nickname,
    #     'email':user.email,
    #     'password':user.password
    # }         #  追求更好的写法

    # return jsonify(r)
    # return jsonify(Wei()) 
    return jsonify(user)  # 替换原本的JSONEncoder ,在user模型下新增 keys 和 __getitem__ 方法

@api.route('', methods = ['PUT'])
def update_user():
    return 'update_user'

@api.route('', methods = ['DELETE'])
def delete_user():
    return 'delete_user'

@api.route('', methods = ['POST'])
def create_user():
    '''
    name,password 数据，第三方，自己的产品，APP，小程序，用户
    人，
    客户端 client
    种类很多
    注册形式很多  短信 邮件 QQ 微信

    '''
    pass