

class Scope:
    allow_api = []
    allow_moudle = []
    forbidden = []
    # def add(self, other):
# 运算符重载，支持对象相加操作
    def __add__(self, other):
        self.allow_api = self.allow_api + other.allow_api
        self.allow_api = list(set(self.allow_api)) # 先转化为set，后转为list 从而去重

        self.allow_moudle = self.allow_moudle + other.allow_moudle
        self.allow_moudle = list(set(self.allow_moudle))   # 模块级别的相加操作

        self.forbidden = self.forbidden + other.forbidden
        self.forbidden = list(set(self.forbidden)) 
        return self


class AdminScope(Scope):
    # allow_api = ['v1.user+super_get_user','v1.user+super_delete_user']  # 因为是注册在Blueprint上，所以endpoint 前缀为 v1 
    
    allow_moudle = ['v1.user']
    # def __init__(self):
    #     self + UserScope()


class UserScope(Scope):
    forbidden =  ['v1.user+super_get_user','v1.user+super_delete_user']
    # allow_api = ['v1.user+get_user','v1.user+delete_user']
    def __init__(self):
        self + AdminScope()




# class SuperScope(Scope):    # 相加操作
#     allow_api = ['v1.C','v1.D']
#     allow_moudle = ['v1.user']

#     def __init__(self):
#         self + UserScope() + AdminScope()



        

    # def add(self, other):
    #     self.allow_api = self.allow_api + other.allow_api
    #     return self  # 将self return不然第二段调用为None.add(),报错
# 提取到基类中，每个都继承这个基类



    # 判断当前访问的endpoint是否在scope中
def is_in_scope(scope, endpoint):
    # 反射获取类
    scope = globals()[scope]()  # globals使用类的名字动态创建对象
    splits = endpoint.split('+')
    red_name = splits[0]
    if endpoint in scope.forbidden:   # 排除
        return False

    if endpoint in scope.allow_api:
        return True
    # v1.view_func  改为v1.moudle_name+view_func  # 改写endpoint
    # 从Redprint 入手  v1.red_name +view_func
    '''
    从   endpoint = options.pop("endpoint", f.__name__)
    改为 endpoint = self.name + '+' + options.pop("endpoint", f.__name__) # 改成Redprint+视图函数名字
            '''
    if red_name in scope.allow_moudle:
        return True
    else:
        return False
    
    # return endpoint in scope.allow_api