from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="Astrology Backend (PyJHora)", version="2.7.0")

app.include_router(router)