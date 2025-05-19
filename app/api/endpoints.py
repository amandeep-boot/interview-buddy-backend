from fastapi import FastAPI, HTTPException ,Depends
from pydantic import BaseModel 
from sqlalchemy.orm import Session
from ..database.models import Message
from ..database.dependencies import get_db 
from groq import Groq
import os
from dotenv import load_dotenv


# Load environment variables
load_dotenv()
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API_KEY not found in .env")

# Initialize Groq client
client = Groq(api_key=api_key)

# Initialize FastAPI app
app = FastAPI()

# Pydantic schema for request body
class Schema(BaseModel):
    user_id: str
    query: str

@app.get("/")
def root():
    return {"message": "This is a chat assistant"}

@app.post("/chat")
async def chat(data: Schema, db: Session = Depends(get_db)):
    system_prompt = "You are a helpful assistant. Answer the user's questions in detail and provide relevant information."

    # Fetch previous messages for the user from the database
    previous_messages = (
        db.query(Message)
        .filter(Message.user_id == data.user_id)
        .order_by(Message.id.asc())
        .all()
    )

    if previous_messages:
        print(f"Previous messages for user {data.user_id}: {[msg.content for msg in previous_messages]}")
    # Prepare messages for Groq API
    messages = [{"role": "system", "content": system_prompt}]
    for msg in previous_messages:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": data.query})

    try:
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=messages,
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )

        response_content = ""
        for chunk in completion:
            response_content += chunk.choices[0].delta.content or ""
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq API error: {str(e)}")

    # Store user and assistant messages in the database
    db.add(Message(user_id=data.user_id, role="user", content=data.query))
    db.add(Message(user_id=data.user_id, role="assistant", content=response_content))
    db.commit()

    return {"response": response_content}