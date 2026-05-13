from types import SimpleNamespace
from unittest.mock import Mock

from app.api.schemas import ReadingCreate
from app.application.ingestion_service import IngestionService


def test_ingest_returns_duplicate_when_idempotency_key_already_exists() -> None:
    service = IngestionService()
    payload = ReadingCreate(
        meter_id="METER-001",
        customer_id="CUSTOMER-001",
        timestamp="2026-05-01T10:00:00+00:00",
        kwh=1.25,
        source="legacy_php",
        quality="measured",
        external_id="reading-001",
    )
    duplicate_row = SimpleNamespace(id=42)
    db = Mock()

    service._find_duplicate = Mock(return_value=duplicate_row)  # type: ignore[method-assign]
    result = service.ingest(db, payload)

    assert result.status == "duplicate"
    assert result.reading_id == 42
    db.add.assert_not_called()
    db.commit.assert_not_called()
