from fastapi import APIRouter , HTTPException , Depends
from fastapi.security import OAuth2PasswordRequestForm
from ...utils.token import create_access_token, verify_google_token, extract_token_info
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

class GoogleLoginRequest(BaseModel):
    id_token: str

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

@app.post("/auth/google")
def google_login(request: GoogleLoginRequest, db: Session = Depends(get_db)):
    # 1. Verify Token 
    payload = verify_google_token(request.id_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid Google token.")
    if not payload.get("email_verified"):
        raise HTTPException(status_code=401, detail="Google email not verified.")
    # 2. Extract the user info from the payload
    sub, email, name, picture = extract_token_info(payload)
    # 3. Check if user exists in the
    user = db.query(User).filter(User.email == email).first()

    if user:
        if user.provider and user.provider != "google":
            raise HTTPException(
            status_code=400,
            detail="This email is already registered with password login."
            )
        user.google_sub = sub
        user.email = email
        user.name = name 
        user.avatar_url = picture
    else:
        user = User(email=email, provider='google', google_sub=sub, name=name, avatar_url=picture)
        db.add(user);
        db.flush()
    
    db.commit()

    # 4. Issue Token
    data = {
        "user_id":user.id
    }
    access_token = create_access_token(data=data)

    response = {
        "access_token":access_token,
        "token_type":"bearer",
        "expires_in":3600
    }
    return response
