from fastapi import FastAPI
from app.api.astrology import router as astrology_router

app = FastAPI(title="Kaira Backend")

app.include_router(astrology_router, prefix="/api")