import json
from pathlib import Path

from pydantic import ValidationError

from app.api.schemas import ReadingCreate
from app.application.ingestion_service import IngestionService
from app.domain.errors import DomainValidationError
from app.domain.models import RejectedReading
from app.infrastructure.database import SessionLocal


SEED_FILES = (
    Path("/seed/sample_readings.json"),
    Path("/seed/sample_readings_with_errors.json"),
)


def _load_seed_payloads() -> list[dict[str, object]]:
    payloads: list[dict[str, object]] = []
    for file_path in SEED_FILES:
        if not file_path.exists():
            continue
        raw = json.loads(file_path.read_text(encoding="utf-8"))
        if isinstance(raw, list):
            payloads.extend(item for item in raw if isinstance(item, dict))
    return payloads


def main() -> None:
    payloads = _load_seed_payloads()
    ingestion_service = IngestionService()
    summary = {"received": 0, "accepted": 0, "duplicates": 0, "rejected": 0}

    db = SessionLocal()
    try:
        for raw_payload in payloads:
            summary["received"] += 1
            try:
                payload = ReadingCreate.model_validate(raw_payload)
            except ValidationError as exc:
                db.add(RejectedReading(raw_payload=raw_payload, reason=str(exc)))
                db.commit()
                summary["rejected"] += 1
                continue

            try:
                result = ingestion_service.ingest(db, payload)
            except DomainValidationError as exc:
                db.add(RejectedReading(raw_payload=raw_payload, reason=str(exc)))
                db.commit()
                summary["rejected"] += 1
                continue

            if result.status == "accepted":
                summary["accepted"] += 1
            elif result.status == "duplicate":
                summary["duplicates"] += 1
    finally:
        db.close()

    print(
        "Seed completed: "
        f"received={summary['received']} "
        f"accepted={summary['accepted']} "
        f"duplicates={summary['duplicates']} "
        f"rejected={summary['rejected']}"
    )


if __name__ == "__main__":
    main()
