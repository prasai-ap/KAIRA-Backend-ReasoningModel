from fastapi import FastAPI
from app.api.astrology_routes import router as astrology_router
from app.api.auth_routes import router as auth_router

app = FastAPI()

app.include_router(astrology_router)
app.include_router(auth_router)