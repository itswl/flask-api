
# from datetime import datetime

# from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy, BaseQuery
# from sqlalchemy import Column, Integer, SmallInteger
# from contextlib import contextmanager


# class SQLAlchemy(_SQLAlchemy):
#     @contextmanager
#     def auto_commit(self):
#         try:
#             yield
#             self.session.commit()
#         except Exception as e:
#             db.session.rollback()
#             raise e

# from app.libs.erro_code import NotFound
# class Query(BaseQuery):
#     def filter_by(self, **kwargs):
#         if 'status' not in kwargs.keys():
#             kwargs['status'] = 1
#         return super(Query, self).filter_by(**kwargs)

#     #  仿照源码改写get_or_404，覆盖原来的 get_or_404]

#     def get_or_404(self, ident):
#         """Like :meth:`get` but aborts with 404 if not found instead of returning ``None``."""

#         rv = self.get(ident)
#         if rv is None:
#             raise NotFound()
#         return rv

#     def first_or_404(self):

#         rv = self.first()
#         if rv is None:
#             raise NotFound()
#         return rv


# db = SQLAlchemy(query_class=Query)


# class Base(db.Model):
#     __abstract__ = True
#     create_time = Column(Integer)
#     status = Column(SmallInteger, default=1)

#     def __init__(self):
#         self.create_time = int(datetime.now().timestamp())

#     @property
#     def create_datetime(self):
#         if self.create_time:
#             return datetime.fromtimestamp(self.create_time)
#         else:
#             return None


#     def __getitem__(self,item):  # 提取到公共类中 base 
#         return getattr(self,item) 


#     def set_attrs(self, attrs_dict):
#         for key, value in attrs_dict.items():
#             if hasattr(self, key) and key != 'id':
#                 setattr(self, key, value)

#     def delete(self):
#         self.status = 0

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy, BaseQuery
from sqlalchemy import inspect, Column, Integer, SmallInteger, orm
from contextlib import contextmanager

from app.libs.erro_code import NotFound

class SQLAlchemy(_SQLAlchemy):
    @contextmanager
    def auto_commit(self):
        try:
            yield
            self.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e


class Query(BaseQuery):
    def filter_by(self, **kwargs):
        if 'status' not in kwargs.keys():
            kwargs['status'] = 1
        return super(Query, self).filter_by(**kwargs)  # status 为 1 才会查询出来

    def get_or_404(self, ident):
        rv = self.get(ident)
        if not rv:
            raise NotFound()
        return rv

    def first_or_404(self):
        rv = self.first()
        if not rv:
            raise NotFound()
        return rv


db = SQLAlchemy(query_class=Query)


class Base(db.Model):
    __abstract__ = True
    create_time = Column(Integer)
    status = Column(SmallInteger, default=1)

    def __init__(self):
        self.create_time = int(datetime.now().timestamp())

    def __getitem__(self, item):
        return getattr(self, item)

    @property
    def create_datetime(self):
        if self.create_time:
            return datetime.fromtimestamp(self.create_time)
        else:
            return None

    def set_attrs(self, attrs_dict):
        for key, value in attrs_dict.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)

    def delete(self):
        self.status = 0

    def keys(self):
        return self.fields

    def hide(self, *keys):
        for key in keys:
            self.fields.remove(key)
        return self

    def append(self, *keys):
        for key in keys:
            self.fields.append(key)
        return self


class MixinJSONSerializer:
    @orm.reconstructor
    def init_on_load(self):
        self._fields = []
        # self._include = []
        self._exclude = []

        self._set_fields()
        self.__prune_fields()

    def _set_fields(self):
        pass

    def __prune_fields(self):
        columns = inspect(self.__class__).columns
        if not self._fields:
            all_columns = set(columns.keys())
            self._fields = list(all_columns - set(self._exclude))

    def hide(self, *args):
        for key in args:
            self._fields.remove(key)
        return self

    def keys(self):
        return self._fields

    def __getitem__(self, key):
        return getattr(self, key)
