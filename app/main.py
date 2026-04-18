from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.api.astrology_routes import router as astrology_router
from app.api.auth_routes import router as auth_router
from app.models.user_astrology_models import UserAstrologyData

app = FastAPI()

app.include_router(astrology_router)
app.include_router(auth_router)