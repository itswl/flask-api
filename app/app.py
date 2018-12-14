

# 之前编写的新的Flask类，JsonEncoder类都是不会轻易改变的，放到app.py中
# 一些其他方法，却是 经常改变的，应该把他们放在init文件中

from flask import Flask as _Flask

from flask.json import JSONEncoder as _JSONEncoder

from app.libs.erro_code import ServerError
from datetime import date

class JSONEncoder(_JSONEncoder):
	def default(self,o):
		# return o.__dict__  # 内置方法，将对象转化为字典  # 缺点是只能转换实例变量，不能将类变量也转换成字典
		# return dict(o) # 考虑不全面.o得有上次定义的那两种方法才不会报错

		if hasattr(o, 'keys') and hasattr(o, '__getitem__'):
			return dict(o)   # 得有这两种方法 才会return dict(o)
		if isinstance(o, date):  # 如果是 时间类型
			return o.strftime('%Y-%m-%d')
		raise ServerError()  # 加多种判断应对不同情况
'''
问题：Python文件运行时报TabError: inconsistent use of tabs and spaces in indentation

原因：说明Python文件中混有Tab和Space用作格式缩进。这通常是使用外部编辑器编辑Python文件时，自动采用Tab进行格式缩进。
拷贝出错
'''


class Flask(_Flask):  # 定义自己的Flask核心对象，继承原来的Flask核心对象
	json_encoder = JSONEncoder # 替换原本的JSONEncoder