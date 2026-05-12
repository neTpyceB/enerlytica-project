from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import ReadingCreate, ReadingIngestResult
from app.application.ingestion_service import IngestionService
from app.domain.errors import DomainValidationError
from app.infrastructure.database import get_db


router = APIRouter(prefix="/api", tags=["readings"])
ingestion_service = IngestionService()


@router.post("/readings", response_model=ReadingIngestResult)
def create_reading(payload: ReadingCreate, db: Session = Depends(get_db)) -> ReadingIngestResult:
    try:
        return ingestion_service.ingest(db, payload)
    except DomainValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
