# app/main.py
from fastapi import FastAPI
from routes.appointments import router as appointment_router
from routes.chat import router as chat_router

app = FastAPI(title="Appointment Booking API")

# Include routes
app.include_router(appointment_router, prefix="/api", tags=["Appointments"])
app.include_router(chat_router, prefix="/api", tags=["Chat"])