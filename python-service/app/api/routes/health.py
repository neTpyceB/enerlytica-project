from fastapi import APIRouter
from sqlalchemy import text

from app.infrastructure.database import SessionLocal


router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def get_health() -> dict[str, str]:
    database_status = "down"

    session = SessionLocal()
    try:
        session.execute(text("SELECT 1"))
        database_status = "up"
    finally:
        session.close()

    return {
        "service": "up",
        "database": database_status,
    }
