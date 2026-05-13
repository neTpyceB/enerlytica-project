from fastapi import FastAPI

from app.api.routes.analytics import router as analytics_router
from app.api.routes.data_quality import router as data_quality_router
from app.api.routes.health import router as health_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.readings import router as readings_router

app = FastAPI(title="Enerlytica Modernization Demo API")
app.include_router(health_router)
app.include_router(readings_router)
app.include_router(jobs_router)
app.include_router(analytics_router)
app.include_router(data_quality_router)
