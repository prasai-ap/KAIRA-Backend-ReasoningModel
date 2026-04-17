from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.schemas.auth_schemas import (
    SendOTPRequest,
    VerifyOTPRequest,
    GoogleLoginRequest,
    TokenResponse,
)
from app.services.auth_service import send_otp, verify_otp, login_with_google

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/send-otp")
def send_otp_route(payload: SendOTPRequest, db: Session = Depends(get_db)):
    return send_otp(db, payload.email)


@router.post("/verify-otp", response_model=TokenResponse)
def verify_otp_route(payload: VerifyOTPRequest, db: Session = Depends(get_db)):
    return verify_otp(db, payload.email, payload.otp)


@router.post("/google", response_model=TokenResponse)
def google_login_route(payload: GoogleLoginRequest, db: Session = Depends(get_db)):
    return login_with_google(db, payload.token)