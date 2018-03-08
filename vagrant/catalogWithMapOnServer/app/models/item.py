from sqlalchemy import Column,Integer,String,ForeignKey,DateTime
from sqlalchemy.orm import relationship
import datetime
from app import Base
from .user import UserProfile

class Item(Base):
    __tablename__ = 'catalogitem'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    category = Column(String)
    user_id = Column(Integer, ForeignKey('userprofile.id'))
    create_date = Column(DateTime, nullable=False, default=datetime.datetime.now)
    last_updated = Column(DateTime, nullable=False, default=datetime.datetime.now,onupdate=datetime.datetime.now)
    user = relationship(UserProfile)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
        'category' : self.category,
        'title' : self.title,
        'id' : self.id,
        'description' : self.description
        
            }
