from datetime import datetime, time as dt_time
import dateparser  
from zoneinfo import ZoneInfo 

# ---- Date parsing & validation ----
def parse_future_date(date_str: str):
    """
    Parses natural language dates and ensures it's today or in the future.
    Returns normalized date string (YYYY-MM-DD) or None if invalid.
    """
    parsed_date = dateparser.parse(date_str)
    if not parsed_date:
        return None

    parsed_date = parsed_date.date()
    today = datetime.today().date()

    if parsed_date >= today:
        return parsed_date.strftime("%Y-%m-%d")
    return None


def is_valid_booking_time(time_str: str, appointment_date: str) -> bool:
    """
    Validates time input is in HH:MM (24-hour) format,
    within 9 AM to 5 PM local time (Asia/Kathmandu),
    and if appointment_date is today, time must be greater than now.
    """
    try:
        # Local timezone
        tz = ZoneInfo("Asia/Kathmandu")

        # Parse time input
        parsed_time = datetime.strptime(time_str.strip(), "%H:%M").time()

        # Business hours
        start = dt_time(9, 0)   # 09:00 AM
        end = dt_time(17, 0)    # 05:00 PM

        # Check time within business hours
        if not (start <= parsed_time <= end):
            return False

        # Check if appointment date is today in local time
        today = datetime.now(tz).date()
        appt_date = datetime.strptime(appointment_date, "%Y-%m-%d").date()

        if appt_date == today:
            now_local_time = datetime.now(tz).time()
            if parsed_time <= now_local_time:
                return False

        return True

    except ValueError:
        return False