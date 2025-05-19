from .database import session_local 
from sqlalchemy.orm import Session
from fastapi import Depends

def get_db():
    db = session_local() 
    try: 
        yield db
        print("Database session yielded")
    finally:
        db.close()
        print("Database session closed")

        