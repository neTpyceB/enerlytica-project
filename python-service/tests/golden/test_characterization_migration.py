import json
from datetime import datetime, timezone
from pathlib import Path

from app.domain.aggregation import aggregate_daily_consumption
from app.domain.models import RawReading, ReadingQuality


def _legacy_php_style_daily_totals(input_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    # Characterization baseline: mirrors a simple legacy loop so migration can prove parity.
    buckets: dict[tuple[str, str], dict[str, object]] = {}
    for item in input_rows:
        timestamp = datetime.fromisoformat(str(item["timestamp"])).astimezone(timezone.utc)
        day = timestamp.date().isoformat()
        key = (str(item["meter_id"]), day)
        if key not in buckets:
            buckets[key] = {
                "meter_id": str(item["meter_id"]),
                "customer_id": str(item["customer_id"]),
                "day": day,
                "total_kwh": 0.0,
                "reading_count": 0,
            }
        buckets[key]["total_kwh"] = float(buckets[key]["total_kwh"]) + float(item["kwh"])
        buckets[key]["reading_count"] = int(buckets[key]["reading_count"]) + 1

    rows = list(buckets.values())
    rows.sort(key=lambda row: (str(row["meter_id"]), str(row["day"])))
    return rows


def test_characterization_legacy_vs_python_aggregation_parity() -> None:
    base_dir = Path(__file__).resolve().parent
    input_rows = json.loads((base_dir / "input_readings.json").read_text(encoding="utf-8"))

    legacy_rows = _legacy_php_style_daily_totals(input_rows)

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
        for item in input_rows
    ]
    python_rows = aggregate_daily_consumption(readings)
    modern_rows = [
        {
            "meter_id": row.meter_id,
            "customer_id": row.customer_id,
            "day": row.day.isoformat(),
            "total_kwh": row.total_kwh,
            "reading_count": row.reading_count,
        }
        for row in python_rows
    ]

    assert modern_rows == legacy_rows
