from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.api.astrology_routes import router as astrology_router
from app.api.auth_routes import router as auth_router
from app.models.user_astrology_models import UserAstrologyData

from app.core.database import SessionLocal
from app.db.session_repository import cleanup_old_revoked_sessions, cleanup_expired_sessions

app = FastAPI()

app.include_router(astrology_router)
app.include_router(auth_router)

@app.on_event("startup")
def cleanup_sessions_on_startup():
    db = SessionLocal()
    try:
        cleanup_old_revoked_sessions(db,days=7)
        cleanup_expired_sessions(db,days=7)
    finally:
        db.close()