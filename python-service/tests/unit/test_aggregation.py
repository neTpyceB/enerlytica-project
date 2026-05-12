from datetime import datetime

from app.domain.aggregation import aggregate_daily_consumption
from app.domain.models import RawReading, ReadingQuality


def test_aggregate_daily_consumption_groups_by_meter_and_utc_day() -> None:
    readings = [
        RawReading(
            meter_id="METER-001",
            customer_id="CUSTOMER-001",
            timestamp=datetime.fromisoformat("2026-05-01T23:30:00+00:00"),
            kwh=1.0,
            source="api",
            quality=ReadingQuality.MEASURED,
        ),
        RawReading(
            meter_id="METER-001",
            customer_id="CUSTOMER-001",
            timestamp=datetime.fromisoformat("2026-05-02T00:15:00+00:00"),
            kwh=2.0,
            source="api",
            quality=ReadingQuality.MEASURED,
        ),
    ]

    result = aggregate_daily_consumption(readings)

    assert len(result) == 2
    assert result[0].meter_id == "METER-001"
    assert result[0].day.isoformat() == "2026-05-01"
    assert result[0].total_kwh == 1.0
    assert result[0].reading_count == 1
    assert result[1].day.isoformat() == "2026-05-02"
    assert result[1].total_kwh == 2.0
