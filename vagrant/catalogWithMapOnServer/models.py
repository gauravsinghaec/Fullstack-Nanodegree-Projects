from sqlalchemy import Column,Integer,String,ForeignKey,DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
import random, string
from itsdangerous import(TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
import datetime

Base = declarative_base()

#You will use this secret key to create and verify your tokens
secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))

class UserProfile(Base):
    __tablename__ = 'userprofile'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), nullable=False)
    password_hash = Column(String(254))
    email = Column(String(250), index=True)
    picture = Column(String(250))
    oauth_user = Column(String(10))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)
    
    #Add a method to generate auth tokens here
    def generate_auth_token(self,expiration=600):
        s = Serializer(secret_key,expires_in=expiration)    
        return s.dumps({'id': self.id})
    
    #Add a method to verify auth tokens here
    @staticmethod
    def verify_auth_token(token):
        s = Serializer(secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        user_id = data['id']
        return user_id

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

class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    title = Column(String(150), nullable=False)
    lattitude = Column(String(10), nullable=False)
    longitude = Column(String(10), nullable=False)

    @property
    def serializeLocations(self):
        #returns object data in serialized format
        return {
            "title": self.title,
            "location" :{"lat": self.lattitude,"lng":self.longitude},
        }

engine = create_engine('postgresql://catalog:catalog@localhost/catalog')
 

Base.metadata.create_all(engine)
