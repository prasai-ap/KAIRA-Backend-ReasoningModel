from fastapi import APIRouter, Depends, Response, Request, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.schemas.auth_schemas import (
    RegisterRequest,
    RegisterVerifyOTPRequest,
    LoginSendOTPRequest,
    LoginVerifyOTPRequest,
    GoogleLoginRequest,
    ResendOTPRequest,
)
from app.services.auth_service import (
    register_user,
    verify_register_otp,
    send_login_otp,
    verify_login_otp,
    login_with_google,
    refresh_tokens,
    logout_user,
    resend_otp,
)
from app.core.security import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


def set_refresh_cookie(response: Response, refresh_token: str):
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False, 
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
    )


def clear_refresh_cookie(response: Response):
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=False,
        samesite="lax",
    )


@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    return register_user(db, payload.full_name, payload.email)


@router.post("/register/verify-otp")
def verify_register(
    payload: RegisterVerifyOTPRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    tokens = verify_register_otp(db, payload.email, payload.otp)
    set_refresh_cookie(response, tokens["refresh_token"])

    return {
        "access_token": tokens["access_token"],
        "token_type": "bearer",
    }


@router.post("/login/send-otp")
def login_send(payload: LoginSendOTPRequest, db: Session = Depends(get_db)):
    return send_login_otp(db, payload.email)


@router.post("/login/verify-otp")
def login_verify(
    payload: LoginVerifyOTPRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    tokens = verify_login_otp(db, payload.email, payload.otp)
    set_refresh_cookie(response, tokens["refresh_token"])

    return {
        "access_token": tokens["access_token"],
        "token_type": "bearer",
    }


@router.post("/google")
def google_login_route(
    payload: GoogleLoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    tokens = login_with_google(db, payload.token)
    set_refresh_cookie(response, tokens["refresh_token"])

    return {
        "access_token": tokens["access_token"],
        "token_type": "bearer",
    }


@router.post("/refresh")
def refresh_token_route(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    tokens = refresh_tokens(db, refresh_token)
    set_refresh_cookie(response, tokens["refresh_token"])

    return {
        "access_token": tokens["access_token"],
        "token_type": "bearer",
    }


@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    refresh_token = request.cookies.get("refresh_token")

    if refresh_token:
        result = logout_user(db, refresh_token)
    else:
        result = {"message": "Logged out successfully"}

    clear_refresh_cookie(response)
    return result

@router.get("/me")
def get_me(user=Depends(get_current_user)):
    return {
        "email": user.email,
        "full_name": user.full_name,
    }

@router.post("/resend-otp")
def resend_otp_route(payload: ResendOTPRequest, db: Session = Depends(get_db)):
    return resend_otp(db, payload.email, payload.purpose)