from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from itertools import pairwise
from typing import Iterable, Protocol


class ReadingLike(Protocol):
    meter_id: str
    timestamp: datetime
    kwh: float
    external_id: str | None


@dataclass(frozen=True)
class DataQualityFinding:
    meter_id: str
    issue_type: str
    description: str
    severity: str


def detect_data_quality_issues(
    readings: Iterable[ReadingLike],
    now: datetime | None = None,
    presorted_by_meter_timestamp: bool = False,
) -> list[DataQualityFinding]:
    now_utc = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    findings: list[DataQualityFinding] = []
    external_id_seen: set[str] = set()
    meter_timestamp_seen: set[tuple[str, datetime]] = set()
    meter_timestamps: dict[str, list[datetime]] = defaultdict(list)
    last_timestamp_by_meter: dict[str, datetime] = {}
    last_timestamp_without_external_id_by_meter: dict[str, datetime] = {}
    max_expected_interval = timedelta(hours=1, minutes=1)

    for reading in readings:
        timestamp_utc = reading.timestamp.astimezone(timezone.utc)
        if reading.kwh < 0:
            findings.append(
                DataQualityFinding(
                    meter_id=reading.meter_id,
                    issue_type="negative_kwh",
                    description=f"Negative kWh reading detected ({reading.kwh}).",
                    severity="high",
                )
            )

        if timestamp_utc > now_utc:
            findings.append(
                DataQualityFinding(
                    meter_id=reading.meter_id,
                    issue_type="future_timestamp",
                    description=f"Reading timestamp {timestamp_utc.isoformat()} is in the future.",
                    severity="medium",
                )
            )
        else:
            if presorted_by_meter_timestamp:
                previous_timestamp = last_timestamp_by_meter.get(reading.meter_id)
                if previous_timestamp is not None and timestamp_utc > previous_timestamp:
                    gap = timestamp_utc - previous_timestamp
                    if gap > max_expected_interval:
                        missing_hours = max(1, int(gap.total_seconds() // 3600) - 1)
                        findings.append(
                            DataQualityFinding(
                                meter_id=reading.meter_id,
                                issue_type="missing_interval",
                                description=(
                                    f"Missing {missing_hours} hourly interval(s) "
                                    f"between {previous_timestamp.isoformat()} and {timestamp_utc.isoformat()}."
                                ),
                                severity="low",
                            )
                        )
                if previous_timestamp is None or timestamp_utc > previous_timestamp:
                    last_timestamp_by_meter[reading.meter_id] = timestamp_utc
            else:
                meter_timestamps[reading.meter_id].append(timestamp_utc)

        if reading.external_id:
            if reading.external_id in external_id_seen:
                findings.append(
                    DataQualityFinding(
                        meter_id=reading.meter_id,
                        issue_type="duplicate_reading",
                        description=f"Duplicate reading detected by external_id={reading.external_id}.",
                        severity="medium",
                    )
                )
            else:
                external_id_seen.add(reading.external_id)
            continue

        if presorted_by_meter_timestamp:
            previous_timestamp = last_timestamp_without_external_id_by_meter.get(reading.meter_id)
            if previous_timestamp == timestamp_utc:
                findings.append(
                    DataQualityFinding(
                        meter_id=reading.meter_id,
                        issue_type="duplicate_reading",
                        description=f"Duplicate reading detected for {reading.meter_id} at {timestamp_utc.isoformat()}.",
                        severity="medium",
                    )
                )
            last_timestamp_without_external_id_by_meter[reading.meter_id] = timestamp_utc
        else:
            key = (reading.meter_id, timestamp_utc)
            if key in meter_timestamp_seen:
                findings.append(
                    DataQualityFinding(
                        meter_id=reading.meter_id,
                        issue_type="duplicate_reading",
                        description=f"Duplicate reading detected for {reading.meter_id} at {timestamp_utc.isoformat()}.",
                        severity="medium",
                    )
                )
            else:
                meter_timestamp_seen.add(key)

    if not presorted_by_meter_timestamp:
        for meter_id, timestamps in meter_timestamps.items():
            ordered = sorted(set(timestamps))
            for previous_timestamp, current_timestamp in pairwise(ordered):
                gap = current_timestamp - previous_timestamp
                if gap > max_expected_interval:
                    missing_hours = max(1, int(gap.total_seconds() // 3600) - 1)
                    findings.append(
                        DataQualityFinding(
                            meter_id=meter_id,
                            issue_type="missing_interval",
                            description=(
                                f"Missing {missing_hours} hourly interval(s) "
                                f"between {previous_timestamp.isoformat()} and {current_timestamp.isoformat()}."
                            ),
                            severity="low",
                        )
                    )

    findings.sort(key=lambda item: (item.meter_id, item.issue_type, item.description))
    return findings
