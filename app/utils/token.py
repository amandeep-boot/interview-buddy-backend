from datetime import datetime, timedelta
from jose.exceptions import JWTError
from dotenv import load_dotenv
from jose import jwt
import os
from google.auth.transport import requests 
from google.oauth2 import id_token

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY environment variable not set.")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
if not GOOGLE_CLIENT_ID:
    raise RuntimeError("GOOGLE_CLIENT_ID environment variable not set.")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def verify_google_token(id_token_str:str):
    """
    Verify google ID token and return payload if valid 
    """
    try:
        payload = id_token.verify_oauth2_token(
            id_token_str,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )
        return payload
    except Exception as e:
        print(f"Token verification failed: {e}")
        return None

def extract_token_info(payload:dict):
    """Extract user info from Google token payload"""
    sub = payload.get('sub')
    email = payload.get('email')
    name = payload.get('name')
    picture = payload.get('picture')
    return sub, email, name, picture