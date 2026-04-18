from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.utils.security import hash_value, verify_hash
from app.db.user_repository import (
    get_user_by_email,
    create_user,
    update_last_login,
)
from app.db.otp_repository import (
    create_otp_record,
    get_latest_otp,
    mark_otp_used,
    create_refresh_session,
    get_refresh_session_by_token_hash,
    revoke_refresh_session,
)
from app.db.session_repository import create_refresh_session
from app.services.otp_service import generate_otp, build_otp_data
from app.services.jwt_service import create_access_token, create_refresh_token
from app.utils.email_utils import send_otp_email
from app.core.auth_config import REFRESH_TOKEN_EXPIRE_DAYS



def _issue_tokens(db: Session, user):
    update_last_login(db, user)

    access_token = create_access_token({"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token({"sub": str(user.id), "email": user.email})

    create_refresh_session(
        db,
        user_id=user.id,
        refresh_token_hash=hash_value(refresh_token),
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        created_at=datetime.now(timezone.utc),
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }



def register_user(db: Session, full_name: str, email: str):
    existing_user = get_user_by_email(db, email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already registered")

    user = create_user(
        db,
        email=email,
        full_name=full_name,
        auth_provider="otp",
    )

    otp = generate_otp()
    otp_data = build_otp_data(email, otp, purpose="register")

    create_otp_record(db, **otp_data)
    print("REGISTER OTP:", otp) 

    send_otp_email(email, otp)

    return {"message": "User registered. OTP sent."}


def verify_register_otp(db: Session, email: str, otp: str):
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp_record = get_latest_otp(db, email, "register")

    if not otp_record or otp_record.used:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if otp_record.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="OTP expired")

    if not verify_hash(otp, otp_record.otp_hash):
        raise HTTPException(status_code=400, detail="Invalid OTP")

    mark_otp_used(db, otp_record)

    return _issue_tokens(db, user)



def send_login_otp(db: Session, email: str):
    user = get_user_by_email(db, email)

    if not user:
        raise HTTPException(status_code=404, detail="User not registered")

    otp = generate_otp()
    otp_data = build_otp_data(email, otp, purpose="login")

    create_otp_record(db, **otp_data)
    print("LOGIN OTP:", otp)  # for testing

    send_otp_email(email, otp)

    return {"message": "OTP sent"}


def verify_login_otp(db: Session, email: str, otp: str):
    user = get_user_by_email(db, email)

    if not user:
        raise HTTPException(status_code=404, detail="User not registered")

    otp_record = get_latest_otp(db, email, "login")

    if not otp_record or otp_record.used:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if otp_record.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="OTP expired")

    if not verify_hash(otp, otp_record.otp_hash):
        raise HTTPException(status_code=400, detail="Invalid OTP")

    mark_otp_used(db, otp_record)

    return _issue_tokens(db, user)

    def logout_user(db: Session, refresh_token: str):
    token_hash = hash_value(refresh_token)
    session = get_refresh_session_by_token_hash(db, token_hash)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found or already logged out")

    revoke_refresh_session(db, session)

    return {"message": "Logged out successfully"}