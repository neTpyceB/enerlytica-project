from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas import AggregateDailyJobResult, JobRunRow
from app.application.job_service import JobService
from app.infrastructure.database import get_db


router = APIRouter(prefix="/api", tags=["jobs"])
job_service = JobService()


@router.post("/jobs/aggregate-daily", response_model=AggregateDailyJobResult)
def aggregate_daily(db: Session = Depends(get_db)) -> AggregateDailyJobResult:
    return job_service.aggregate_daily_consumption(db)


@router.get("/jobs", response_model=list[JobRunRow])
def list_jobs(db: Session = Depends(get_db)) -> list[JobRunRow]:
    rows = job_service.list_job_runs(db)
    return [JobRunRow.model_validate(row, from_attributes=True) for row in rows]
