from .endpoints.auth import  signup , login
from .endpoints.chat import chat , root , upload_resume,upload_job_description
from fastapi import APIRouter


app_router = APIRouter()
app_router.post("/auth/signup")(signup)
app_router.post("/auth/login")(login)
app_router.get("/")(root) 
app_router.post("/chat")(chat)
app_router.post("/chat/upload/resume")(upload_resume)
app_router.post("/chat/upload/jd")(upload_job_description)

