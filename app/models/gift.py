

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
