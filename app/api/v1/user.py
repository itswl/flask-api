
# from flask import Blueprint

# user = Blueprint('user',__name__)

# @user.route('/v1/user/get')
# def get_user():
#     return 'imwl'

from app.libs.redprint import Redprint
from app.libs.token_auth import auth
from app.models.user import User
from app.models.base import db
from flask import jsonify ,g

from app.libs.erro_code import DeleteSuccess, AuthFailed

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
# 管理员账户
@api.route('/<int:uid>', methods = ['GET'])  # 获取到用户的uid
@auth.login_required
def super_get_user(uid):   # 接收 uid
    # user = User.query.get_or_404 (uid)  #获取到用户，用get_or_404简化判断用户是否存在
                                # 因为get_or_404 抛出的不是APIException,所以要重写
                                # query 属性下的方法 
    user = User.query.filter_by(id=uid).first_or_404()
    # r = {
    #     'nickname':user.nickname,
    #     'email':user.email,
    #     'password':user.password
    # }         #  追求更好的写法

    # return jsonify(r)
    # return jsonify(Wei()) 
    return jsonify(user)  # 替换原本的JSONEncoder ,在user模型下新增 keys 和 __getitem__ 方法

# 普通 账户  需要从token拿到uid
@api.route('', methods = ['GET'])   
@auth.login_required
def get_user():
    uid = g.user.uid 
    user = User.query.filter_by(id=uid).first_or_404()
    return jsonify(user)



@api.route('', methods = ['PUT'])
def update_user():
    return 'update_user'

# 普通账号
@api.route('', methods = ['DELETE'])   
@auth.login_required
def delete_user():
    uid = g.user.uid   #  防止超权，从token中读取  已存储在 g 变量中 ，g 变量线程隔离。
                    # 对于管理员来说，可以超权，删除别的用户

    with db.auto_commit():

        # user = User.query.get_or_404(uid)   #软删除后，用get 还是能查询到，所以改写
        user = User.query.filter_by(id=uid).first_or_404()
        user.delete()     #  软删除
    # return 'delete sucess'
    return DeleteSuccess()

# 管理员  
# 创建方式 ，普通注册，改auth 为2
# 离线脚本  fake.py
@api.route('/<int:uid>', methods=['DELETE'])
def super_delete_user(uid):
    with db.auto_commit():
        user=User.query.filter_by(id=uid).first_or_404()
        user.delete()
        return DeleteSuccess()


# @api.route('', methods = ['POST'])
# def create_user():
#     '''
#     name,password 数据，第三方，自己的产品，APP，小程序，用户
#     人，
#     客户端 client
#     种类很多
#     注册形式很多  短信 邮件 QQ 微信

#     '''
#     pass