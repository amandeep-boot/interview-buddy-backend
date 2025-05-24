from sqlalchemy import Column, Integer, String
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer , primary_key = True , index =True)
    email = Column(String , unique = True , index = True )
    hashed_password = Column(String) 

class Message(Base):
    __tablename__ = "chat_history" 
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String) 
    role = Column(String)
    content = Column(String)
