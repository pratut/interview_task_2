# routes/chat.py
from fastapi import APIRouter

from models.chat import chain_with_history, get_redis_history
from models.entries import ChatRequest, ChatResponse
from models.mail import send_email
from models.book_validator import parse_future_date, is_valid_booking_time
from models.redis_helper import get_booking_state, set_booking_state, clear_booking_state, normalize, is_booking_trigger

from config.constants import ADMIN_EMAIL, BOOKING_FIELDS_ORDER, EMAIL_REGEX, PHONE_REGEX
from config.pinecone_db  import pinecone_index

from sentence_transformers import SentenceTransformer

import re
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo 
from dotenv import load_dotenv


load_dotenv()

router = APIRouter()
current_time = datetime.now(ZoneInfo("Asia/Kathmandu")).strftime("%H:%M")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")



@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Chat endpoint with Redis-based memory and booking flow.
    Supports:
      - "bye" to end session
      - Booking flow triggered by multiple phrases
      - Name, email, phone, date (natural language), and message collection
      - Email confirmations to both customer & admin
      - Fallback to LLM for regular chat
    """
    history = get_redis_history(request.session_id)
    redis_client = history.redis_client
    user_msg = normalize(request.question)

    # End session
    if user_msg == "bye":
        history.clear()
        clear_booking_state(redis_client, request.session_id)
        return ChatResponse(answer="Goodbye! Your session has ended.")

    # Continue booking flow
    booking_state = get_booking_state(redis_client, request.session_id)
    if booking_state.get("booking_started"):
        for field in BOOKING_FIELDS_ORDER:
            if field not in booking_state:
                user_input = request.question.strip()

                # Validate email
                if field == "email" and not re.match(EMAIL_REGEX, user_input):
                    return ChatResponse(answer="That doesn't look like a valid email. Please enter a valid email address.")

                # Validate phone
                if field == "phone" and not re.match(PHONE_REGEX, user_input):
                    return ChatResponse(answer="That doesn't look like a valid phone number. Please enter a valid phone number.")

                # Validate & normalize date
                if field == "date":
                    normalized_date = parse_future_date(user_input)
                    if not normalized_date:
                        today = date.today()
                        tomorrow = today + timedelta(days=1)
                        return ChatResponse(answer=f"Please provide a valid future date (e.g., 'next Monday' or {tomorrow}).")
                    user_input = normalized_date  # store normalized format
                # Validate time
                if field == "time":
                    booking_date = booking_state.get("date")
                    if not booking_date:
                        return ChatResponse(answer="Please provide the date before specifying the time.")
                    if not is_valid_booking_time(user_input, booking_date):
                        current_time = datetime.now(ZoneInfo("Asia/Kathmandu")).strftime("%H:%M")
                        return ChatResponse(
                            answer=f"Please provide a valid time between 09:00 and 17:00, "
                                f"and if it's today, choose a time later than now {current_time}."
                        )

                # Save field
                set_booking_state(redis_client, request.session_id, **{field: user_input})

                # Ask next question or finish booking
                next_index = BOOKING_FIELDS_ORDER.index(field) + 1
                if next_index < len(BOOKING_FIELDS_ORDER):
                    next_field = BOOKING_FIELDS_ORDER[next_index]
                    prompt_map = {
                        "name": "What's your name?",
                        "email": "What's your email address?",
                        "phone": "What's your phone number?",
                        "date": "What date should I book?",
                        "time": "What time do you prefer? Please provide in 24-hour format (e.g., 14:30).",
                        "message": "Any message you'd like to include?"
                    }
                    return ChatResponse(answer=prompt_map[next_field])

                # Booking complete
                final_data = get_booking_state(redis_client, request.session_id)
                customer_body = (
                    f"Hello {final_data['name']},\n\nYour appointment is confirmed.\n"
                    f"📅 Date: {final_data['date']}\n"
                    f"⏰ Time: {final_data['time']}\n"
                    f"📞 Phone: {final_data['phone']}\n\n"
                    "Best regards,\nAppointment Team"
                )
                admin_body = (
                    f"New appointment booked:\n"
                    f"👤 Name: {final_data['name']}\n"
                    f"📧 Email: {final_data['email']}\n"
                    f"📞 Phone: {final_data['phone']}\n"
                    f"📅 Date: {final_data['date']}\n"
                    f"⏰ Time: {final_data['time']}\n"
                    f"📝 Message: {final_data['message']}"
                )

                send_email(final_data["email"], "Appointment Confirmation", customer_body)
                send_email(ADMIN_EMAIL, "New Appointment", admin_body)
                
                booking_text = (
                    f"Name: {final_data['name']}, Email: {final_data['email']}, Phone: {final_data['phone']}, "
                    f"Date: {final_data['date']}, Time: {final_data['time']}, Message: {final_data['message']}"
                )
                
                embedding = model.encode(booking_text, convert_to_tensor=False)
                
                pinecone_index.upsert([
                    {
                        "id": f"{request.session_id}-{final_data['date']}-{final_data['time']}",
                        "values": embedding,
                        "metadata": final_data
                    }
                ])
                
                
                clear_booking_state(redis_client, request.session_id)
                return ChatResponse(answer=f"✅ Appointment booked for {final_data['date']} and confirmation sent to {final_data['email']}.")

    # Detect booking intent
    if is_booking_trigger(user_msg):
        set_booking_state(redis_client, request.session_id, booking_started="1")
        return ChatResponse(answer="Sure! What's your name?")

    # Fallback to regular chat
    result = chain_with_history.invoke(
        {"question": request.question},
        config={"configurable": {"session_id": request.session_id}}
    )
    return ChatResponse(answer=result.content)
