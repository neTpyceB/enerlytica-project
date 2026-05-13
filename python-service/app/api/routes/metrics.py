from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.models import JobRun, RawReading, RejectedReading
from app.infrastructure.database import get_db
from app.infrastructure.metrics import METRICS, render_prometheus_text


router = APIRouter(prefix="/api", tags=["metrics"])


@router.get("/metrics", response_class=PlainTextResponse)
def get_metrics(db: Session = Depends(get_db)) -> PlainTextResponse:
    counters, gauges = METRICS.snapshot()

    raw_readings_count = db.scalar(select(func.count()).select_from(RawReading)) or 0
    rejected_readings_count = db.scalar(select(func.count()).select_from(RejectedReading)) or 0
    gauges["enerlytica_raw_readings_stored_total"] = float(raw_readings_count)
    gauges["enerlytica_rejected_readings_stored_total"] = float(rejected_readings_count)

    latest_completed_run = db.scalar(
        select(JobRun)
        .where(
            JobRun.job_name == "aggregate_daily_consumption",
            JobRun.status == "completed",
        )
        .order_by(JobRun.finished_at.desc(), JobRun.id.desc())
        .limit(1)
    )
    if (
        latest_completed_run is not None
        and latest_completed_run.started_at is not None
        and latest_completed_run.finished_at is not None
    ):
        gauges["enerlytica_last_successful_aggregation_timestamp_seconds"] = latest_completed_run.finished_at.timestamp()
        gauges["enerlytica_aggregation_duration_seconds"] = (
            latest_completed_run.finished_at - latest_completed_run.started_at
        ).total_seconds()

    latest_reading_timestamp = db.scalar(select(func.max(RawReading.timestamp)))
    if latest_reading_timestamp is None:
        gauges["enerlytica_data_freshness_seconds"] = -1.0
    else:
        freshness_seconds = (
            datetime.now(timezone.utc) - latest_reading_timestamp.astimezone(timezone.utc)
        ).total_seconds()
        gauges["enerlytica_data_freshness_seconds"] = max(0.0, freshness_seconds)

    body = render_prometheus_text(counters=counters, gauges=gauges)
    return PlainTextResponse(body, media_type="text/plain; version=0.0.4; charset=utf-8")
