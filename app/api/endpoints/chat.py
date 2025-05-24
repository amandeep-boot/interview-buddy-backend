from ...utils.dependency import get_current_user, extract_json_response
from fastapi import FastAPI, HTTPException ,Depends
from ...database.models import Message, UserData
from ...database.dependencies import get_db 
from fastapi import File, UploadFile
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from pydantic import BaseModel 
from pathlib import Path
from groq import Groq
import json
import fitz  # PyMuPDF
import os

# Load environment variables
load_dotenv()
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API_KEY not found in .env")

# Initialize Groq client
client = Groq(api_key=api_key)

SYSTEM_PROMPT_PATH = Path(__file__).parent.parent.parent / "templates" / "chat-prompt.txt"
with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()
# Initialize FastAPI app
app = FastAPI()

# Pydantic schema for request body
class Schema(BaseModel):
    query: str

@app.get("/")
def root():
    return {"message": "This is a chat assistant"}

@app.post("/chat")
async def chat(data: Schema, db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    # Step 1: Fetch resume & JD for this user
    user_data = db.query(UserData).filter(UserData.user_id == user_id).first()
    resume_text = user_data.resume_text if user_data and user_data.resume_text else "User has not uploaded a resume."
    job_description = user_data.job_description if user_data and user_data.job_description else "No job description provided."

    context_input = {
        "resume_text": resume_text,
        "job_description": job_description,
        "interaction_type": "followup" if data.query.strip() else "initial",
        "user_input": data.query.strip() if data.query.strip() else None
    }

    previous_messages = (
        db.query(Message)
            .filter(Message.user_id == user_id)
            .order_by(Message.id.desc())  # newest first
            .limit(10)
            .all()
    )[::-1]  # reverse to restore chronological order

    # system_prompt = SYSTEM_PROMPT + "\n\n" + f"INPUT:\n```json\n{context_input}\n```
    system_prompt = SYSTEM_PROMPT + "\n\nINPUT:\n```json\n" + json.dumps(context_input, indent=2) + "\n```"

    # Step 3: Prepare messages for Groq API
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

    # Step 4: Store interaction
    db.add(Message(user_id=user_id, role="user", content=data.query))
    db.add(Message(user_id=user_id, role="assistant", content=response_content))
    db.commit()

    # print(f"Response {response_content}")
    parsed_response = extract_json_response(response_content)
    return parsed_response

@app.post("/chat/upload/resume")
async def upload_resume(
    resume: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    if resume.content_type not in ["application/pdf", "text/plain"]:
        raise HTTPException(status_code=400, detail="Invalid resume file type. Only PDF and text files are allowed.")
    if resume.content_type == "application/pdf":
        pdf_document = fitz.open(stream=await resume.read(), filetype="pdf")
        resume_text = "\n".join(page.get_text() for page in pdf_document)
    else:
        resume_text = (await resume.read()).decode("utf-8")
    user_data = db.query(UserData).filter(UserData.user_id == user_id).first()
    if not user_data:
        user_data = UserData(user_id=user_id, resume_text=resume_text)
        db.add(user_data)
    else:
        user_data.resume_text = resume_text
    db.commit()
    return {"message": "Resume uploaded successfully."}
@app.post("/chat/upload/jd")
async def upload_job_description(
    job_description: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    if job_description.content_type not in ["application/pdf", "text/plain"]:
        raise HTTPException(status_code=400, detail="Invalid job description file type. Only PDF and text files are allowed.")
    if job_description.content_type == "application/pdf":
        pdf_document = fitz.open(stream=await job_description.read(), filetype="pdf")
        job_description_text = "\n".join(page.get_text() for page in pdf_document)
    else:
        job_description_text = (await job_description.read()).decode("utf-8")
    user_data = db.query(UserData).filter(UserData.user_id == user_id).first()
    if not user_data:
        user_data = UserData(user_id=user_id, job_description=job_description_text)
        db.add(user_data)
    else:
        user_data.job_description = job_description_text
    db.commit()
    return {"message": "Job description uploaded successfully."}
