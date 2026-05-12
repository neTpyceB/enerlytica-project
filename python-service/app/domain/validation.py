from app.domain.errors import DomainValidationError


def validate_reading_payload(meter_id: str, customer_id: str, source: str) -> None:
    if not meter_id.strip():
        raise DomainValidationError("meter_id is required")

    if not customer_id.strip():
        raise DomainValidationError("customer_id is required")

    if not source.strip():
        raise DomainValidationError("source is required")
