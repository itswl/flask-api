

![直接return q 时](https://upload-images.jianshu.io/upload_images/14597179-430f03fc7686561d.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)


会报内置错误，因为在body中指定了json格式。可以更改为slient模式


app\validators\base.py
```

'''
1.代码太啰嗦了，每个试图函数里，都需要这么写

2.ClientTypeError只是代表客户端类型异常，其他的参数校验不通过也抛出这个异常的话不合适

为了解决上面的问题，我们需要重写wtforms

定义一个自定义BaseForm，让其他的Form来继承
'''
from wtforms import Form
from app.libs.erro_code import ParameterException
from flask import request,jsonify

class BaseForm(Form):
    # def __init__(self, data):
    def __init__(self):
        # data = request.json
        data = request.get_json(silent = True)  #  出现错误，不报异常
        args = request.args.to_dict()  # 完成查询参数的获取
        super(BaseForm, self).__init__(data=data,**args)   # 调用父类构造函数

    def validate_for_api(self):
        valid = super(BaseForm, self).validate()  # 调用父类的构造方法 # 验证是否通过
        if not valid:   # 没通过
            # 所有异常类信息在form errors 中 
            raise ParameterException(msg=self.errors) #  抛出异常  # 公共的自定义异常类
        return self
```
搜索界面不需要返回全部字段，详情页面则返回全部字段。可以在app\modles\book.py中隐藏
```
from sqlalchemy import Column, String, Integer, orm

from app.models.base import Base



class Book(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(50), nullable=False)
    author = Column(String(30), default='未名')
    binding = Column(String(20))
    publisher = Column(String(50))
    price = Column(String(20))
    pages = Column(Integer)
    pubdate = Column(String(20))
    isbn = Column(String(15), nullable=False, unique=True)
    summary = Column(String(1000))
    image = Column(String(50))

    fields = ['id', 'title', 'author', 'binding',
                        'publisher',
                        'price','pages', 'pubdate', 'isbn',
                        'summary',
                        'image']

    def keys(self):
        return self.fields

    def hide(self,key):  
        self.fields.remove(key)
        return self

```
**第一次能够隐藏成功，而第二次会受到第一次的影响从而隐藏失败**
**因为改动的是类变量**
改动如下：
```
from sqlalchemy import Column, String, Integer, orm

from app.models.base import Base



class Book(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(50), nullable=False)
    author = Column(String(30), default='未名')
    binding = Column(String(20))
    publisher = Column(String(50))
    price = Column(String(20))
    pages = Column(Integer)
    pubdate = Column(String(20))
    isbn = Column(String(15), nullable=False, unique=True)
    summary = Column(String(1000))
    image = Column(String(50))

    # fields = ['id', 'title', 'author', 'binding',
    #                    'publisher',
    #                    'price','pages', 'pubdate', 'isbn',
    #                    'summary',
    #                    'image']
    
    '''
    第一次能够隐藏成功，而第二次会受到第一次的影响从而隐藏失败。
    因为改动的是类变量,改写如下:
    '''
 
    @orm.reconstructor  
    # 因为通过sqlalchemy创建的构造函数不会被执行，通过这个装饰器构造函数可以执行  
    # 这就是有追求的啊
    def __init__(self):
        self.fields = ['id', 'title', 'author', 'binding',
                       'publisher',
                       'price','pages', 'pubdate', 'isbn',
                       'summary',
                       'image']   # 定义成实例变量。

    def keys(self):
        return self.fields

    def hide(self,*keys):  # 支持隐藏多个关键字
        for key in keys:
            self.fields.remove(key)
        return self
```
并非只有book模型需要隐藏字段，所以可以提取到base基类中,同理，还可以追加append.

```
from sqlalchemy import Column, String, Integer, orm

from app.models.base import Base



class Book(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(50), nullable=False)
    author = Column(String(30), default='未名')
    binding = Column(String(20))
    publisher = Column(String(50))
    price = Column(String(20))
    pages = Column(Integer)
    pubdate = Column(String(20))
    isbn = Column(String(15), nullable=False, unique=True)
    summary = Column(String(1000))
    image = Column(String(50))

    @orm.reconstructor  
    def __init__(self):
        self.fields = ['id', 'title', 'author', 'binding',
                       'publisher',
                       'price','pages', 'pubdate', 'isbn',
                       'summary',
                       'image']   # 定义成实例变量。

```
app\api\v1\book.py
```
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
    books=Book.query.filter(or_(Book.title.like(q),Book.publisher.like(q))).all()  
#like 指定关键字 q
    books=[book.hide('summary','id').append('pages') for book in books]   
# 只 返回指定的 关键字
    # 隐藏summary，id.追加pages.
    return jsonify(books)

@api.route('/<int:isbn>/detail')
def detail(isbn):
    book=Book.query.filter_by(isbn=isbn).first_or_404()  
# detail 中可以返回所有字段
    return jsonify(book)
```
### 新建礼gift模型
app\models\gift.py
```
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base



class Gift(Base):
    id = Column(Integer, primary_key=True)
    
    # 建立和user关系
    user = relationship('User')
    uid = Column(Integer, ForeignKey('user.id'))

    isbn = Column(String(15), nullable=False)
    launched = Column(Boolean, default=False)

```
app\api\v1\gift.py
```
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

```
为token新增一个接口验证是否过期
```
@api.route('/secret', methods=['POST'])
def get_token_info():
    """获取令牌信息"""
    form = TokenForm().validate_for_api()
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(form.token.data, return_header=True)  # 不报错就是合法的token
    except SignatureExpired:
        raise AuthFailed(msg='token is expired', erro_code=1003)
    except BadSignature:
        raise AuthFailed(msg='token is invalid', erro_code=1002)

    r = {
        'scope': data[0]['scope'],
        'create_at': data[1]['iat'],  # 创建时间
        'expire_in': data[1]['exp'],   # 过期时间
        'uid': data[0]['uid']
    } # 把令牌信息读取出来，以明文方式返回到客户端去
    # 自定义返回字段，甚至不返回，只提供验证功能
    return jsonify(r)
```
![](https://upload-images.jianshu.io/upload_images/14597179-66943d92f81d0cdd.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

![](https://upload-images.jianshu.io/upload_images/14597179-a5d2f999a87ddc3d.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
