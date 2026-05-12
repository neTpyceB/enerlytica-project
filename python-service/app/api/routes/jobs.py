from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas import AggregateDailyJobResult
from app.application.job_service import JobService
from app.infrastructure.database import get_db


router = APIRouter(prefix="/api", tags=["jobs"])
job_service = JobService()


@router.post("/jobs/aggregate-daily", response_model=AggregateDailyJobResult)
def aggregate_daily(db: Session = Depends(get_db)) -> AggregateDailyJobResult:
    return job_service.aggregate_daily_consumption(db)
