from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.api.astrology_routes import router as astrology_router
from app.api.auth_routes import router as auth_router
from app.models.user_astrology_models import UserAstrologyData
from app.api.chat_routes import router as chat_router
from app.models.chat_models import ChatSession, ChatMessage

from app.core.database import SessionLocal
from app.db.session_repository import cleanup_revoked_sessions, cleanup_expired_sessions
from app.db.otp_repository import cleanup_otps

app = FastAPI()

app.include_router(astrology_router)
app.include_router(auth_router)
app.include_router(chat_router)

@app.on_event("startup")
def cleanup_sessions_on_startup():
    db = SessionLocal()
    try:
        cleanup_revoked_sessions(db)
        cleanup_expired_sessions(db,days=7)
        cleanup_otps(db)
    finally:
        db.close()