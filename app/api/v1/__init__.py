
from flask import Blueprint
from app.api.v1 import user, book ,client

 #  创建一个Bluerint,把Redprint注册到Blueprint上，并传入Redprint一个前缀'/book
def create_blueprint_v1():
    bp_v1 = Blueprint('v1', __name__) 

    user.api.register(bp_v1)  # , url_prefix='/uesr')
    book.api.register(bp_v1)  # ,url_prefix='/book')
    client.api.register(bp_v1)
    return bp_v1