import os
from dotenv import load_dotenv
from slowapi import Limiter
from slowapi.util import get_remote_address

load_dotenv()

def get_rate_limit_key(request):
    user = getattr(request.state, "user", None)

    if user:
        return str(user.id)

    return get_remote_address(request)


limiter = Limiter(key_func=get_rate_limit_key)

LOGIN_RATE_LIMIT = os.getenv("LOGIN_RATE_LIMIT")
REGISTER_RATE_LIMIT = os.getenv("REGISTER_RATE_LIMIT")
REFRESH_RATE_LIMIT = os.getenv("REFRESH_RATE_LIMIT")
CHAT_RATE_LIMIT = os.getenv("CHAT_RATE_LIMIT")
ASTROLOGY_RATE_LIMIT = os.getenv("ASTROLOGY_RATE_LIMIT")
GENERAL_RATE_LIMIT = os.getenv("GENERAL_RATE_LIMIT")