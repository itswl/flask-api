
 #  用来测试字典序列化

r = {'name': 'weilai'}  # 直接定义一个字典

r = dict(name= 'weilai') # 使用dict函数

class Wei():
    name = 'weilai'
    age = 'age'

    def __init__(self):
        self.gender = 'male'

    def keys(self):   
        return ('name','age','gender')  #  取到 key ,  做到自定义key 
        # # return ('name',)  # 一个元素的元组
        # return ['name']  # return 序列类型的都可以

    def __getitem__(self,item):  
        return getattr(self,item)   # 取到 key对应的value

o = Wei()
print(dict(o))