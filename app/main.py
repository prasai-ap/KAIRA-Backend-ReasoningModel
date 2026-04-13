from fastapi import FastAPI
from app.api.astrology_routes import router as astrology_router

app = FastAPI(title="Astrology Backend (PyJHora)", version="2.7.0")

app.include_router(astrology_router)