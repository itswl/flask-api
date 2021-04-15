from flask_restful import Api
from flask import Blueprint
from app.api.v1.test import Hello


def register_views(app):
    api = Api(app)
    api.add_resource(Hello, '/hello', endpoint="hello")

def  create_blueprint_v1():
    bp_v1 = Blueprint('v1', __name__)
    register_views(bp_v1)
    return bp_v1
