import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import ReadingCreate, ReadingIngestResult
from app.application.ingestion_service import IngestionService
from app.domain.errors import DomainValidationError
from app.infrastructure.database import get_db
from app.infrastructure.metrics import METRICS


router = APIRouter(prefix="/api", tags=["readings"])
ingestion_service = IngestionService()
logger = logging.getLogger(__name__)


@router.post("/readings", response_model=ReadingIngestResult)
def create_reading(payload: ReadingCreate, db: Session = Depends(get_db)) -> ReadingIngestResult:
    METRICS.inc_counter("enerlytica_records_received_total")
    try:
        result = ingestion_service.ingest(db, payload)
    except DomainValidationError as exc:
        METRICS.inc_counter("enerlytica_records_rejected_total")
        logger.warning("reading_rejected")
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if result.status == "accepted":
        METRICS.inc_counter("enerlytica_records_accepted_total")
    elif result.status == "duplicate":
        METRICS.inc_counter("enerlytica_duplicates_detected_total")

    logger.info(f"reading_{result.status}")
    return result
