from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timezone
from typing import Sequence

from app.domain.models import RawReading


@dataclass(frozen=True)
class DailyAggregation:
    meter_id: str
    customer_id: str
    day: date
    total_kwh: float
    reading_count: int


def aggregate_daily_consumption(readings: Sequence[RawReading]) -> list[DailyAggregation]:
    buckets: dict[tuple[str, date], dict[str, float | int | str]] = defaultdict(
        lambda: {"customer_id": "", "total_kwh": 0.0, "reading_count": 0}
    )

    for reading in readings:
        day = reading.timestamp.astimezone(timezone.utc).date()
        key = (reading.meter_id, day)

        if buckets[key]["customer_id"] == "":
            buckets[key]["customer_id"] = reading.customer_id

        buckets[key]["total_kwh"] += reading.kwh
        buckets[key]["reading_count"] += 1

    results: list[DailyAggregation] = []
    for (meter_id, day), payload in buckets.items():
        results.append(
            DailyAggregation(
                meter_id=meter_id,
                customer_id=str(payload["customer_id"]),
                day=day,
                total_kwh=float(payload["total_kwh"]),
                reading_count=int(payload["reading_count"]),
            )
        )

    results.sort(key=lambda item: (item.meter_id, item.day))
    return results
