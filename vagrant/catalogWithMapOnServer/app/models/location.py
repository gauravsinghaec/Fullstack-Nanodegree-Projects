from sqlalchemy import Column,Integer,String
from app import Base

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
