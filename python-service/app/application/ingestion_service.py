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

        reading = RawReading(
            meter_id=payload.meter_id,
            customer_id=payload.customer_id,
            timestamp=payload.timestamp,
            kwh=payload.kwh,
            source=payload.source,
            quality=payload.quality,
            external_id=payload.external_id,
        )
        db.add(reading)
        db.commit()
        db.refresh(reading)

        return ReadingIngestResult(
            status="accepted",
            reading_id=reading.id,
        )
