
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

    # def keys(self):
    #     return self.fields

    # def hide(self,*keys):  # 支持隐藏多个关键字
    #     for key in keys:
    #         self.fields.remove(key)
    #     return self
      #  提取到base基类中

