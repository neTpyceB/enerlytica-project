from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.readings import router as readings_router

app = FastAPI(title="Enerlytica Modernization Demo API")
app.include_router(health_router)
app.include_router(readings_router)
