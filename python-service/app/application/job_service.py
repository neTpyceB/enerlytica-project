from datetime import datetime, timezone
import logging

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.api.schemas import AggregateDailyJobResult
from app.domain.aggregation import aggregate_daily_consumption
from app.domain.data_quality import detect_data_quality_issues
from app.domain.models import DataQualityIssue, DailyConsumption, JobRun, RawReading
from app.infrastructure.metrics import METRICS


logger = logging.getLogger(__name__)


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
            readings = db.scalars(select(RawReading)).all()
            daily_rows = aggregate_daily_consumption(readings)
            if daily_rows:
                calculated_at = datetime.now(timezone.utc)
                rows = [
                    {
                        "meter_id": item.meter_id,
                        "customer_id": item.customer_id,
                        "day": item.day,
                        "total_kwh": item.total_kwh,
                        "reading_count": item.reading_count,
                        "calculated_at": calculated_at,
                    }
                    for item in daily_rows
                ]

                statement = pg_insert(DailyConsumption).values(rows)
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

            findings = detect_data_quality_issues(readings, now=started_at)
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
            job_run.records_processed = len(readings)
            job_run.records_failed = 0
            job_run.message = (
                f"Aggregated {len(daily_rows)} daily rows; detected {len(findings)} data quality issues."
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
            readings_processed=len(readings),
            days_aggregated=len(daily_rows),
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
