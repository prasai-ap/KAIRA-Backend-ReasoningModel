from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr


class RegisterVerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str


class LoginSendOTPRequest(BaseModel):
    email: EmailStr


class LoginVerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str


class GoogleLoginRequest(BaseModel):
    token: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class ResendOTPRequest(BaseModel):
    email: EmailStr
    purpose: str