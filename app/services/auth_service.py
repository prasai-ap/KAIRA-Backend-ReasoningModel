from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.auth_config import REFRESH_TOKEN_EXPIRE_DAYS
from app.utils.security import hash_value, verify_hash
from app.db.user_repository import (
    get_user_by_email,
    get_user_by_google_sub,
    create_user,
    update_last_login,
)
from app.db.otp_repository import (
    create_otp_record,
    get_latest_otp,
    mark_otp_used,
    increment_attempt_count,
)
from app.db.session_repository import create_refresh_session
from app.services.otp_service import generate_otp, build_otp_data
from app.services.jwt_service import create_access_token, create_refresh_token
from app.services.google_auth_service import verify_google_token
from app.utils.email_utils import send_otp_email


def send_otp(db: Session, email: str):
    otp = generate_otp()
    otp_data = build_otp_data(email, otp)
    create_otp_record(db, **otp_data)
    send_otp_email(email, otp)
    return {"message": "OTP sent successfully"}


def verify_otp(db: Session, email: str, otp: str):
    otp_record = get_latest_otp(db, email)

    if not otp_record:
        raise HTTPException(status_code=404, detail="OTP not found")

    if otp_record.used:
        raise HTTPException(status_code=400, detail="OTP already used")

    if otp_record.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="OTP expired")

    if not verify_hash(otp, otp_record.otp_hash):
        increment_attempt_count(db, otp_record)
        raise HTTPException(status_code=400, detail="Invalid OTP")

    mark_otp_used(db, otp_record)

    user = get_user_by_email(db, email)
    if not user:
        user = create_user(db, email=email, auth_provider="otp")

    update_last_login(db, user)

    access_token = create_access_token({"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token({"sub": str(user.id), "email": user.email})

    create_refresh_session(
        db,
        user_id=user.id,
        refresh_token_hash=hash_value(refresh_token),
        device_info=None,
        ip_address=None,
        user_agent=None,
        is_revoked=False,
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        created_at=datetime.now(timezone.utc),
        revoked_at=None,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def login_with_google(db: Session, token: str):
    info = verify_google_token(token)

    email = info.get("email")
    google_sub = info.get("google_sub")
    full_name = info.get("full_name")

    if not email:
        raise HTTPException(status_code=400, detail="Google account email not found")

    user = get_user_by_google_sub(db, google_sub)

    if not user:
        user = get_user_by_email(db, email)

    if not user:
        user = create_user(
            db,
            email=email,
            full_name=full_name,
            auth_provider="google",
            google_sub=google_sub,
        )
    else:
        if not user.google_sub:
            user.google_sub = google_sub
            db.commit()
            db.refresh(user)

    update_last_login(db, user)

    access_token = create_access_token({"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token({"sub": str(user.id), "email": user.email})

    create_refresh_session(
        db,
        user_id=user.id,
        refresh_token_hash=hash_value(refresh_token),
        device_info=None,
        ip_address=None,
        user_agent=None,
        is_revoked=False,
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        created_at=datetime.now(timezone.utc),
        revoked_at=None,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }