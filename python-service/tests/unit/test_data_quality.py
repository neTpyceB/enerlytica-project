from datetime import datetime, timezone

from app.domain.data_quality import detect_data_quality_issues
from app.domain.models import RawReading, ReadingQuality


def test_detect_data_quality_issues_flags_duplicate_future_and_missing_interval() -> None:
    readings = [
        RawReading(
            meter_id="METER-001",
            customer_id="CUSTOMER-001",
            timestamp=datetime.fromisoformat("2026-05-01T10:00:00+00:00"),
            kwh=1.0,
            source="api",
            quality=ReadingQuality.MEASURED,
            external_id="ext-1",
        ),
        RawReading(
            meter_id="METER-001",
            customer_id="CUSTOMER-001",
            timestamp=datetime.fromisoformat("2026-05-01T12:00:00+00:00"),
            kwh=1.1,
            source="api",
            quality=ReadingQuality.MEASURED,
            external_id="ext-1",
        ),
        RawReading(
            meter_id="METER-001",
            customer_id="CUSTOMER-001",
            timestamp=datetime.fromisoformat("2026-05-03T08:00:00+00:00"),
            kwh=0.9,
            source="api",
            quality=ReadingQuality.MEASURED,
        ),
    ]

    findings = detect_data_quality_issues(
        readings,
        now=datetime(2026, 5, 2, 0, 0, tzinfo=timezone.utc),
    )

    issue_types = {item.issue_type for item in findings}
    assert "duplicate_reading" in issue_types
    assert "future_timestamp" in issue_types
    assert "missing_interval" in issue_types
