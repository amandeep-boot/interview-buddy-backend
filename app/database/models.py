from sqlalchemy import Column, Integer, String
from .database import Base

class Message(Base):
    __tablename__ = "chat_history" 
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String) 
    role = Column(String)
    content = Column(String)
