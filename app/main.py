from fastapi.middleware.cors import CORSMiddleware
from .database.database import Base, engine
from .api.routes import app_router
from .database.models import Message
from fastapi import FastAPI

app = FastAPI()
app.add_middleware( 
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


Base.metadata.create_all(bind=engine)


app.include_router(app_router)