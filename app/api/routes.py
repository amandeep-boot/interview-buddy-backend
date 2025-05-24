from fastapi import APIRouter
from .endpoints.chat import chat , root 
from .endpoints.auth import  signup , login


app_router = APIRouter()
app_router.post("/auth/signup")(signup)
app_router.post("/auth/login")(login)
app_router.get("/")(root) 
app_router.post("/chat")(chat)
# app_router.post("/chat/upload")(upload_pdf)
#     db.add(Message(user_id="file_upload", role="file", content=content))  
#     db.commit()   


