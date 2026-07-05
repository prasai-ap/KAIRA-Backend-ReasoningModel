from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.astrology_routes import router as astrology_router
from app.api.auth_routes import router as auth_router
from app.api.chat_routes import router as chat_router
from app.api.payment_routes import router as payment_router

from app.core.database import SessionLocal
from app.db.session_repository import cleanup_revoked_sessions, cleanup_expired_sessions
from app.db.otp_repository import cleanup_otps

from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

from app.core.rate_limit import limiter

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(astrology_router)
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(payment_router)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

@app.on_event("startup")
def cleanup_sessions_on_startup():
    db = SessionLocal()
    try:
        cleanup_revoked_sessions(db)
        cleanup_expired_sessions(db,days=7)
        cleanup_otps(db)
    finally:
        db.close()
