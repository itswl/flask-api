

from flask import g

from app.libs.erro_code import Success, DuplicateGift
from app.libs.redprint import Redprint
from app.libs.token_auth import auth
from app.models.base import db
from app.models.book import Book
from app.models.gift import Gift

# 得去app\api\v1\__init__.py注册到Blueprint

api = Redprint('gift')   


@api.route('/<isbn>', methods=['POST'])
@auth.login_required
def create(isbn):
    uid = g.user.uid  # 拿到当前需要赠送礼物的uid号
    with db.auto_commit():
        Book.query.filter_by(isbn=isbn).first_or_404()  #检测是否是在数据库中
        gift = Gift.query.filter_by(isbn=isbn, uid=uid).first()
        if gift:   # 检测是否重复
            raise DuplicateGift()
        gift = Gift()
        gift.isbn = isbn
        gift.uid = uid
        db.session.add(gift)
    return Success()




