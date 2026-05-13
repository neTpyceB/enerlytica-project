from datetime import datetime, timezone
from dataclasses import dataclass
import logging

from sqlalchemy import Date, cast, delete, func, literal, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.api.schemas import AggregateDailyJobResult
from app.domain.data_quality import detect_data_quality_issues
from app.domain.models import DataQualityIssue, DailyConsumption, JobRun, RawReading
from app.infrastructure.metrics import METRICS


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class _DataQualityReading:
    meter_id: str
    timestamp: datetime
    kwh: float
    external_id: str | None


class JobService:
    def aggregate_daily_consumption(self, db: Session) -> AggregateDailyJobResult:
        started_at = datetime.now(timezone.utc)
        METRICS.inc_counter("enerlytica_aggregation_runs_total")
        job_run = JobRun(
            job_name="aggregate_daily_consumption",
            started_at=started_at,
            status="running",
            records_processed=0,
            records_failed=0,
        )
        db.add(job_run)
        db.commit()
        db.refresh(job_run)

        try:
            readings_processed = int(db.scalar(select(func.count()).select_from(RawReading)) or 0)
            day_expr = cast(func.timezone("UTC", RawReading.timestamp), Date)
            aggregated_readings = (
                select(
                    RawReading.meter_id.label("meter_id"),
                    func.min(RawReading.customer_id).label("customer_id"),
                    day_expr.label("day"),
                    func.sum(RawReading.kwh).label("total_kwh"),
                    func.count(RawReading.id).label("reading_count"),
                )
                .group_by(RawReading.meter_id, day_expr)
                .subquery()
            )
            days_aggregated = int(db.scalar(select(func.count()).select_from(aggregated_readings)) or 0)

            if days_aggregated > 0:
                calculated_at = datetime.now(timezone.utc)
                statement = pg_insert(DailyConsumption).from_select(
                    [
                        "meter_id",
                        "customer_id",
                        "day",
                        "total_kwh",
                        "reading_count",
                        "calculated_at",
                    ],
                    select(
                        aggregated_readings.c.meter_id,
                        aggregated_readings.c.customer_id,
                        aggregated_readings.c.day,
                        aggregated_readings.c.total_kwh,
                        aggregated_readings.c.reading_count,
                        literal(calculated_at),
                    ),
                )
                upsert = statement.on_conflict_do_update(
                    index_elements=[DailyConsumption.meter_id, DailyConsumption.day],
                    set_={
                        "customer_id": statement.excluded.customer_id,
                        "total_kwh": statement.excluded.total_kwh,
                        "reading_count": statement.excluded.reading_count,
                        "calculated_at": statement.excluded.calculated_at,
                    },
                )
                db.execute(upsert)

            quality_rows = db.execute(
                select(
                    RawReading.meter_id,
                    RawReading.timestamp,
                    RawReading.kwh,
                    RawReading.external_id,
                )
                .order_by(RawReading.meter_id.asc(), RawReading.timestamp.asc(), RawReading.id.asc())
                .execution_options(yield_per=1_000)
            )
            findings = detect_data_quality_issues(
                (
                    _DataQualityReading(
                        meter_id=row.meter_id,
                        timestamp=row.timestamp,
                        kwh=row.kwh,
                        external_id=row.external_id,
                    )
                    for row in quality_rows
                ),
                now=started_at,
                presorted_by_meter_timestamp=True,
            )
            db.execute(delete(DataQualityIssue))
            if findings:
                db.add_all(
                    [
                        DataQualityIssue(
                            meter_id=item.meter_id,
                            issue_type=item.issue_type,
                            description=item.description,
                            severity=item.severity,
                        )
                        for item in findings
                    ]
                )

            job_run.finished_at = datetime.now(timezone.utc)
            job_run.status = "completed"
            job_run.records_processed = readings_processed
            job_run.records_failed = 0
            job_run.message = (
                f"Aggregated {days_aggregated} daily rows; detected {len(findings)} data quality issues."
            )
            db.commit()

            duration_seconds = (job_run.finished_at - started_at).total_seconds()
            METRICS.set_gauge("enerlytica_aggregation_duration_seconds", duration_seconds)
            METRICS.set_gauge(
                "enerlytica_last_successful_aggregation_timestamp_seconds",
                job_run.finished_at.timestamp(),
            )
            logger.info("aggregation_job_completed")
        except Exception:
            METRICS.inc_counter("enerlytica_aggregation_failures_total")
            db.rollback()
            job_run.finished_at = datetime.now(timezone.utc)
            job_run.status = "failed"
            job_run.records_processed = 0
            job_run.records_failed = 1
            job_run.message = "Aggregation failed"
            db.add(job_run)
            db.commit()
            logger.exception("aggregation_job_failed")
            raise

        return AggregateDailyJobResult(
            status="completed",
            readings_processed=readings_processed,
            days_aggregated=days_aggregated,
        )

    def list_job_runs(self, db: Session, limit: int = 50) -> list[JobRun]:
        return list(
            db.scalars(
                select(JobRun).order_by(JobRun.started_at.desc(), JobRun.id.desc()).limit(limit)
            ).all()
        )

    def list_data_quality_issues(self, db: Session, limit: int = 200) -> list[DataQualityIssue]:
        return list(
            db.scalars(
                select(DataQualityIssue)
                .order_by(DataQualityIssue.detected_at.desc(), DataQualityIssue.id.desc())
                .limit(limit)
            ).all()
        )
