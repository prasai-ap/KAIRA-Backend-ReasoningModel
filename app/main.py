from fastapi import FastAPI

from app.api.routes_charts import router as charts_router
from app.api.routes_dasha import router as dasha_router
from app.api.routes_yoga import router as yoga_router
from app.api.routes_dosha import router as dosha_router

app = FastAPI(title="Astrology Backend (PyJHora)", version="2.7.0")

app.include_router(charts_router, prefix="/api")
app.include_router(dasha_router, prefix="/api")
app.include_router(yoga_router, prefix="/api")
app.include_router(dosha_router, prefix="/api")