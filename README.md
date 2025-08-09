# Palm Mind Interview Task 2

# RAG-based agentic system -- LangChain + Redis + SMTP + PineCone

## 🗨️ FastAPI Chat & Appointment Booking System

A **FastAPI**-based chatbot with **Redis-powered conversation history** and an integrated **appointment booking flow**.  
Supports **name, email, phone, date, time, and message collection** with validation for:
- ✅ Email format  
- ✅ Phone format  
- ✅ Date parsing (must be in the future)  
- ✅ Time parsing (must be between 9 AM and 5 PM, and later than current time if booking is today)  
- ✅ Automatic confirmation emails to customer and admin  
- ✅ Updates booking info to pinecone database with embedding (sentence-transformer)
---

## 🚀 Features

- **Natural conversation** with memory stored in Redis
- **Trigger words detection** for booking (e.g., `"book appointment"`, `"schedule meeting"`, `"reserve"`, `"appointment"`, etc.)
- **Step-by-step booking form** through chat
- **Smart date & time validation** using `dateparser` and Python’s `datetime`
- **Email notifications** using SMTP
- **Session handling** for multiple users
- **Clear session on "bye"**

---



## 📦 Installation  

### 1️⃣ Clone the repository  
```bash
git clone https://github.com/pratut/interview_task_2.git
cd interview_task
```


2️⃣ Create and activate a virtual environment
```
python -m venv .venv
source .venv/bin/activate 
```

3️⃣ Copy environment template and configure
```
cp .env_template .env
```

4️⃣ Install dependencies
```
pip install -r requirements.txt
```

▶️ Run the application
```
uvicorn main:app --reload
```

### API Endpoints
## POST /chat
Request
```
{
    "session_id": "user123",
    "question": "Book appointment"
}
```
Response:
```
{
    "answer": "Sure! What's your name?"
}