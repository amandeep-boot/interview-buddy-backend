from fastapi import APIRouter , HTTPException , Depends
from fastapi.security import OAuth2PasswordRequestForm
from ...utils.token import create_access_token
from ...database.dependencies import get_db
from pydantic import BaseModel , EmailStr 
from passlib.context import CryptContext
from ...database.models import User 
from sqlalchemy.orm import Session 


app = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"],deprecated = "auto")

class SignUpSchema(BaseModel):
    email:EmailStr
    password :str 

@app.post("/auth/signup")
async def signup(data : SignUpSchema , db:Session= Depends(get_db)):
    # check if user already exists 
    existing_user = db.query(User).filter(User.email== data.email).first()
    if existing_user:
        raise HTTPException(status_code= 400 , detail= "Email already registered." )
    
    # hash password 
    hashed_password = pwd_context.hash(data.password) 

    # Createeee and store new user 

    new_user = User(email = data.email , hashed_password = hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user) 

    return {"message" : "User registered successfully."} 


class LoginRequest(BaseModel):
    email:EmailStr
    password :str 

@app.post("/auth/Login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password.")

    if not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password.")

    access_token = create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}