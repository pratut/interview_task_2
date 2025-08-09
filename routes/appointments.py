#routes/appointments.py
from fastapi import APIRouter, HTTPException
from models.entries import AppointmentRequest
from models.mail import send_email
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
EMAIL_ADDRESS = os.environ['ADMIN_EMAIL']

@router.post("/book-appointment")
def book_appointment(request: AppointmentRequest):
    # 1️⃣ Customer Confirmation Email
    customer_email_body = (
        f"Hello {request.name},\n\n"
        f"Your appointment has been booked successfully.\n"
        f"📅 Date: {request.date}\n"
        f"⏰ Time: {request.time}\n\n"
        "We look forward to seeing you!\n\n"
        "Best regards,\nAppointment Team"
    )

    # 2️⃣ Admin Notification Email
    admin_email_body = (
        f"📢 New Appointment Confirmed\n\n"
        f"Name: {request.name}\n"
        f"Email: {request.email}\n"
        f"Phone: {request.phone}\n"
        f"Date: {request.date}\n"
        f"Time: {request.time}\n"
        f"Message: {request.message}\n"
    )

    customer_sent = send_email(request.email, "Appointment Confirmation", customer_email_body)
    admin_sent = send_email(EMAIL_ADDRESS, f"New Appointment with {request.name}", admin_email_body)

    if customer_sent and admin_sent:
        return {"status": "success", "message": "Appointment booked. Emails sent to customer and admin."}
    else:
        raise HTTPException(status_code=500, detail="Failed to send one or more emails.")
