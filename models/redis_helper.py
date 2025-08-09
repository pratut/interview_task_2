from config.constants import BOOKING_KEY_PREFIX, BOOKING_TRIGGERS

# ---- Redis helpers ----
def get_booking_state(redis_client, session_id: str) -> dict:
    key = f"{BOOKING_KEY_PREFIX}{session_id}"
    state = redis_client.hgetall(key)
    return {
        (k.decode() if isinstance(k, bytes) else k):
        (v.decode() if isinstance(v, bytes) else v)
        for k, v in state.items()
    } if state else {}

def set_booking_state(redis_client, session_id: str, **kwargs) -> None:
    key = f"{BOOKING_KEY_PREFIX}{session_id}"
    redis_client.hset(key, mapping=kwargs)

def clear_booking_state(redis_client, session_id: str) -> None:
    key = f"{BOOKING_KEY_PREFIX}{session_id}"
    redis_client.delete(key)

def normalize(text: str) -> str:
    return text.strip().lower()

def is_booking_trigger(message: str) -> bool:
    msg = normalize(message)
    return any(trigger in msg for trigger in BOOKING_TRIGGERS)