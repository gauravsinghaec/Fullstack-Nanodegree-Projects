from sqlalchemy import Column,Integer,String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context

Base = declarative_base()

class UserProfile(Base):
    __tablename__ = 'userprofile'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), nullable=False)
    password_hash = Column(String(64))
    email = Column(String(250), index=True)
    picture = Column(String(250))
    oauth_user = Column(String(10))


class Item(Base):
    __tablename__ = 'catalogitem'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    category = Column(String)
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
        'title' : self.title,
        'description' : self.description,
        'category' : self.category
            }

engine = create_engine('sqlite:///catalog.db')
 

Base.metadata.create_all(engine)
