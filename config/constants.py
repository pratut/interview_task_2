#confid/constants.py
import os


# ---- Constants ----
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
BOOKING_KEY_PREFIX = "booking_state:"
BOOKING_TRIGGERS = {
    "book appointment", "schedule appointment", "set up appointment",
    "make appointment", "book meeting", "schedule meeting",
    "book a call", "schedule a call", "appointment request",
    "reserve appointment", "reserve meeting", "set meeting",
    "booking", "schedule", "reserve", "book me","book","ok"
}

BOOKING_FIELDS_ORDER = ["name", "email", "phone", "date","time", "message"]

EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$"
PHONE_REGEX = r"^\+?\d[\d\-\s]{7,}$"  # Allows +, -, spaces