from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.schemas.auth_schemas import (
    RegisterRequest,
    RegisterVerifyOTPRequest,
    LoginSendOTPRequest,
    LoginVerifyOTPRequest,
    GoogleLoginRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from app.services.auth_service import (
    register_user,
    verify_register_otp,
    send_login_otp,
    verify_login_otp,
    login_with_google,
    logout_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    return register_user(db, payload.full_name, payload.email)


@router.post("/register/verify-otp", response_model=TokenResponse)
def verify_register(payload: RegisterVerifyOTPRequest, db: Session = Depends(get_db)):
    return verify_register_otp(db, payload.email, payload.otp)


@router.post("/login/send-otp")
def login_send(payload: LoginSendOTPRequest, db: Session = Depends(get_db)):
    return send_login_otp(db, payload.email)


@router.post("/login/verify-otp", response_model=TokenResponse)
def login_verify(payload: LoginVerifyOTPRequest, db: Session = Depends(get_db)):
    return verify_login_otp(db, payload.email, payload.otp)


@router.post("/google", response_model=TokenResponse)
def google_login_route(payload: GoogleLoginRequest, db: Session = Depends(get_db)):
    return login_with_google(db, payload.token)


@router.post("/logout")
def logout(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    return logout_user(db, payload.refresh_token)