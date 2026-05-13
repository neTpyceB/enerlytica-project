from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas import DataQualityIssueRow
from app.application.job_service import JobService
from app.infrastructure.database import get_db


router = APIRouter(prefix="/api", tags=["data-quality"])
job_service = JobService()


@router.get("/data-quality/issues", response_model=list[DataQualityIssueRow])
def list_data_quality_issues(db: Session = Depends(get_db)) -> list[DataQualityIssueRow]:
    rows = job_service.list_data_quality_issues(db)
    return [DataQualityIssueRow.model_validate(row, from_attributes=True) for row in rows]
