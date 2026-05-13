import pytest
from pydantic import ValidationError

from app.api.schemas import ReadingCreate
from app.domain.errors import DomainValidationError
from app.domain.validation import validate_reading_payload


def test_schema_rejects_timezone_naive_timestamp() -> None:
    with pytest.raises(ValidationError):
        ReadingCreate(
            meter_id="METER-001",
            customer_id="CUSTOMER-001",
            timestamp="2026-05-01T10:00:00",
            kwh=1.25,
            source="legacy_php",
            quality="measured",
        )


def test_schema_rejects_negative_kwh() -> None:
    with pytest.raises(ValidationError):
        ReadingCreate(
            meter_id="METER-001",
            customer_id="CUSTOMER-001",
            timestamp="2026-05-01T10:00:00+00:00",
            kwh=-0.1,
            source="legacy_php",
            quality="measured",
        )


def test_schema_rejects_infinite_kwh() -> None:
    with pytest.raises(ValidationError):
        ReadingCreate(
            meter_id="METER-001",
            customer_id="CUSTOMER-001",
            timestamp="2026-05-01T10:00:00+00:00",
            kwh=float("inf"),
            source="legacy_php",
            quality="measured",
        )


def test_schema_rejects_overlong_external_id() -> None:
    with pytest.raises(ValidationError):
        ReadingCreate(
            meter_id="METER-001",
            customer_id="CUSTOMER-001",
            timestamp="2026-05-01T10:00:00+00:00",
            kwh=1.25,
            source="legacy_php",
            quality="measured",
            external_id="x" * 129,
        )


def test_schema_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        ReadingCreate(
            meter_id="METER-001",
            customer_id="CUSTOMER-001",
            timestamp="2026-05-01T10:00:00+00:00",
            kwh=1.25,
            source="legacy_php",
            quality="measured",
            unexpected="value",
        )


def test_domain_validation_rejects_blank_meter_id() -> None:
    with pytest.raises(DomainValidationError):
        validate_reading_payload(
            meter_id="   ",
            customer_id="CUSTOMER-001",
            source="legacy_php",
        )
