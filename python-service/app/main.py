import uuid

from fastapi import FastAPI, Request

from app.api.routes.analytics import router as analytics_router
from app.api.routes.data_quality import router as data_quality_router
from app.api.routes.health import router as health_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.metrics import router as metrics_router
from app.api.routes.readings import router as readings_router
from app.infrastructure.logging import bind_request_id, configure_logging, reset_request_id

configure_logging()
app = FastAPI(title="Enerlytica Modernization Demo API")


@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    token = bind_request_id(request_id)
    try:
        response = await call_next(request)
    finally:
        reset_request_id(token)

    response.headers["x-request-id"] = request_id
    return response


app.include_router(health_router)
app.include_router(readings_router)
app.include_router(jobs_router)
app.include_router(analytics_router)
app.include_router(data_quality_router)
app.include_router(metrics_router)
