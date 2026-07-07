from fastapi import APIRouter, Depends, Response, Request, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.schemas.auth_schemas import (
    RegisterRequest,
    RegisterVerifyOTPRequest,
    LoginSendOTPRequest,
    LoginVerifyOTPRequest,
    GoogleLoginRequest,
    ResendOTPRequest,
    MeResponse,
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
    get_me_profile,
)
from app.core.security import get_current_user
from app.services.profile_image_service import upload_profile_image
from app.db.user_repository import update_user_profile_image
from app.core.rate_limit import (
    limiter,
    REGISTER_RATE_LIMIT,
    LOGIN_RATE_LIMIT,
    REFRESH_RATE_LIMIT,
)

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
@limiter.limit(REGISTER_RATE_LIMIT)
def register(request: Request, payload: RegisterRequest, db: Session = Depends(get_db)):
    return register_user(db, payload.full_name, payload.email)


@router.post("/register/verify-otp")
@limiter.limit("5/minute")
def verify_register(
    request: Request,
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
@limiter.limit(LOGIN_RATE_LIMIT)
def login_send(request: Request, payload: LoginSendOTPRequest, db: Session = Depends(get_db)):
    return send_login_otp(db, payload.email)


@router.post("/login/verify-otp")
@limiter.limit("5/minute")
def login_verify(
    request: Request,
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
@limiter.limit("10/minute")
def google_login_route(
    request: Request,
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
@limiter.limit(REFRESH_RATE_LIMIT)
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

@router.get("/me", response_model=MeResponse)
def me(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return get_me_profile(db, user)

@router.post("/resend-otp")
@limiter.limit("3/minute")
def resend_otp_route(request: Request, payload: ResendOTPRequest, db: Session = Depends(get_db)):
    return resend_otp(db, payload.email, payload.purpose)

@router.post("/me/profile-image")
@limiter.limit("10/hour")
def update_my_profile_image(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    image_url = upload_profile_image(file, str(user.id))
    updated_user = update_user_profile_image(db, user, image_url)

    return {
        "message": "Profile image updated successfully",
        "profile_image_url": updated_user.profile_image_url,
    }