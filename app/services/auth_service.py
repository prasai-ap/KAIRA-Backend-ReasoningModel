from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.utils.security import hash_value, verify_hash
from app.db.user_repository import (
    get_user_by_email,
    create_user,
    update_last_login,
    get_user_by_google_sub,
    get_user_by_id,
)
from app.db.otp_repository import (
    create_otp_record,
    get_latest_otp,
    mark_otp_used,
)
from app.db.session_repository import (
    create_refresh_session,
    get_refresh_session_by_token_hash,
    revoke_refresh_session,
    revoke_all_user_sessions,
)
from app.services.otp_service import generate_otp, build_otp_data
from app.services.jwt_service import create_access_token, create_refresh_token
from app.services.google_auth_service import verify_google_token
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
        is_revoked=False,
        revoked_at=None,
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
    print("LOGIN OTP:", otp)
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

    return _issue_tokens(db, user)


def refresh_tokens(db: Session, refresh_token: str):
    token_hash = hash_value(refresh_token)
    session = get_refresh_session_by_token_hash(db, token_hash)

    if not session:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expired")

    user = get_user_by_id(db, str(session.user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    revoke_refresh_session(db, session)

    access_token = create_access_token({"sub": str(user.id), "email": user.email})
    new_refresh_token = create_refresh_token({"sub": str(user.id), "email": user.email})

    create_refresh_session(
        db,
        user_id=user.id,
        refresh_token_hash=hash_value(new_refresh_token),
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        created_at=datetime.now(timezone.utc),
        is_revoked=False,
        revoked_at=None,
    )

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


def logout_user(db: Session, refresh_token: str):
    token_hash = hash_value(refresh_token)
    session = get_refresh_session_by_token_hash(db, token_hash)

    if not session:
        raise HTTPException(status_code=400, detail="Session not found or already logged out")

    revoked_count = revoke_all_user_sessions(db, session.user_id)

    return {
        "message": "Logged out Successfully",
        "revoked_sessions": revoked_count,
    }