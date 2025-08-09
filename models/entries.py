#models/entries.py
from pydantic import BaseModel, EmailStr

class AppointmentRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    date: str
    time: str
    message: str
    
    
class ChatRequest(BaseModel):
    session_id: str
    question: str

class ChatResponse(BaseModel):
    answer: str