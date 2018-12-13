
# 模仿Blueprint构建一个Redprint

# 红图的实现可以模仿蓝图的实现结构 ，
# 由于红图的route里没有办法拿到蓝图的对象，
# 所以我们可以先把他们存储起来，等碰到的时候再进行注册

class Redprint:
    def __init__(self,name):
        self.name = name 
        self.mound = []

    def route(self, rule, **options):
        def decorator(f):
            self.mound.append((f, rule, options))
            return f
        return decorator

    # 在register方法中可以获取到蓝图对象，
    # 所以之前route中视图函数的注册延迟到这里进行
    def register(self, bp,  url_prefix = None):
    # 如果不传url_prefix 则默认使用name
        if url_prefix is None:
            url_prefix = '/'+self.name   # 定义 Redprint 前缀
        # python的自动拆包
        for f, rule, options in self.mound:
            endpoint = options.pop("endpoint", f.__name__)
            # 将视图函数注册到蓝图上来
            bp.add_url_rule(url_prefix + rule, endpoint, f, **options)

'''
流程梳理
模仿Blueprint自定义Redprint
app/api/v1/book.py中实例化一个Redprint 来注册视图函数。
app/api/v1/__init__.py 中创建一个Bluerint,把Redprint注册到Blueprint上，并传入Redprint一个前缀'/book'
在app/__init__.py 中 将Blueprint注册到flask核心对象上,并传入一个前缀'/v1'

'''