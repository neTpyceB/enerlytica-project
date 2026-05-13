import json
from datetime import datetime
from pathlib import Path

from app.domain.aggregation import aggregate_daily_consumption
from app.domain.models import RawReading, ReadingQuality


def test_golden_daily_aggregation_output_matches_expected_dataset() -> None:
    base_dir = Path(__file__).resolve().parent
    input_readings = json.loads((base_dir / "input_readings.json").read_text(encoding="utf-8"))
    expected_rows = json.loads((base_dir / "expected_daily_consumption.json").read_text(encoding="utf-8"))

    readings = [
        RawReading(
            meter_id=item["meter_id"],
            customer_id=item["customer_id"],
            timestamp=datetime.fromisoformat(item["timestamp"]),
            kwh=item["kwh"],
            source=item["source"],
            quality=ReadingQuality(item["quality"]),
            external_id=item.get("external_id"),
        )
        for item in input_readings
    ]

    result = aggregate_daily_consumption(readings)
    actual_rows = [
        {
            "meter_id": item.meter_id,
            "customer_id": item.customer_id,
            "day": item.day.isoformat(),
            "total_kwh": item.total_kwh,
            "reading_count": item.reading_count,
        }
        for item in result
    ]

    assert actual_rows == expected_rows
