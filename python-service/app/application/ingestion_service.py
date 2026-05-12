from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.schemas import ReadingCreate, ReadingIngestResult
from app.domain.models import RawReading
from app.domain.validation import validate_reading_payload


class IngestionService:
    def ingest(self, db: Session, payload: ReadingCreate) -> ReadingIngestResult:
        validate_reading_payload(
            meter_id=payload.meter_id,
            customer_id=payload.customer_id,
            source=payload.source,
        )

        existing = self._find_duplicate(db, payload)
        if existing is not None:
            return ReadingIngestResult(
                status="duplicate",
                reading_id=existing.id,
            )

        reading = RawReading(
            meter_id=payload.meter_id,
            customer_id=payload.customer_id,
            timestamp=payload.timestamp,
            kwh=payload.kwh,
            source=payload.source,
            quality=payload.quality.value,
            external_id=payload.external_id,
        )
        db.add(reading)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            existing = self._find_duplicate(db, payload)
            if existing is not None:
                return ReadingIngestResult(
                    status="duplicate",
                    reading_id=existing.id,
                )
            raise

        db.refresh(reading)

        return ReadingIngestResult(
            status="accepted",
            reading_id=reading.id,
        )

    def _find_duplicate(self, db: Session, payload: ReadingCreate) -> RawReading | None:
        if payload.external_id is not None:
            return db.scalar(
                select(RawReading).where(RawReading.external_id == payload.external_id)
            )

        return db.scalar(
            select(RawReading).where(
                RawReading.meter_id == payload.meter_id,
                RawReading.timestamp == payload.timestamp,
            )
        )
