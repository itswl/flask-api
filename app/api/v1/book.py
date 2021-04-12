## 使用蓝图
# from flask import Blueprint

# book = Blueprint('book',__name__)

# @book.route('/v1/book/get')
# def get_book():
#     return 'hello world'



from flask import jsonify
from sqlalchemy import or_  # 模糊查询 或

from app.libs.redprint import Redprint
from app.models.book import Book
from app.validators.forms import BookSearchForm

api=Redprint('book')

@api.route('/create')
def create_book():
    return 'create_book'
@api.route('/get')
def get_book():
    return 'get book'
@api.route('/search')
def search():
    #url http://locahost:5000/v1/book/search?q={}
    # request.args.to_dict() 在base中完成
    form = BookSearchForm().validate_for_api() #  完成验证
    q='%'+form.q.data+'%'  # 模糊搜索前后得加 %
    # return q
    books=Book.query.filter(or_(Book.title.like(q),Book.publisher.like(q))).all()  #like 指定关键字 q
    books=[book.hide('summary','id').append('pages') for book in books]   # 只 返回指定的 关键字
    # 隐藏summary，id.追加pages.
    return jsonify(books)

@api.route('/<int:isbn>/detail')
def detail(isbn):
    book=Book.query.filter_by(isbn=isbn).first_or_404()  # detail 中可以返回所有字段
    return jsonify(book)