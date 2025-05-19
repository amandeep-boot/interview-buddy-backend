from fastapi import APIRouter
from .endpoints import chat , root 

app_router = APIRouter()

app_router.get("/")(root) 
app_router.post("/chat")(chat)


