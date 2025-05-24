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
    user_id = Column(Integer, index=True ) 
    role = Column(String)
    content = Column(String)

class UserData(Base):
    __tablename__ = "user_data"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    resume_text = Column(String)
    job_description = Column(String)
