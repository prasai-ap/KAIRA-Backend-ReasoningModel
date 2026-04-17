import random
from datetime import datetime, timedelta, timezone

from app.core.auth_config import OTP_EXPIRE_MINUTES
from app.utils.security import hash_value


def generate_otp() -> str:
    return str(random.randint(100000, 999999))


def build_otp_data(email: str, otp: str) -> dict:
    now = datetime.now(timezone.utc)
    return {
        "email": email,
        "otp_hash": hash_value(otp),
        "purpose": "login",
        "expires_at": now + timedelta(minutes=OTP_EXPIRE_MINUTES),
        "used": False,
        "attempt_count": 0,
        "created_at": now,
    }