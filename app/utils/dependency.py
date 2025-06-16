from fastapi import Depends , HTTPException , status
from fastapi.security import OAuth2PasswordBearer
from .token import decode_access_token
import json
import re
oauth2_scheme = OAuth2PasswordBearer(tokenUrl= "/auth/login")

def get_current_user(token :str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if payload is None :
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid or expired token ",
            headers= {"WWW-Authenticate": "Bearer"},    
        )
    return payload["user_id"]


def extract_json_response(text: str):
    import json, re
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to extract the first JSON-looking object
        match = re.search(r"\{[\s\S]*?\}", text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    # 🛠 fallback: wrap raw text in "response"
    return {"response": text.strip()}
