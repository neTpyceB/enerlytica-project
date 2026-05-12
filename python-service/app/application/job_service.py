from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.api.schemas import AggregateDailyJobResult
from app.domain.aggregation import aggregate_daily_consumption
from app.domain.models import DailyConsumption, RawReading


class JobService:
    def aggregate_daily_consumption(self, db: Session) -> AggregateDailyJobResult:
        readings = db.scalars(select(RawReading)).all()
        daily_rows = aggregate_daily_consumption(readings)

        if daily_rows:
            now = datetime.now(timezone.utc)
            rows = [
                {
                    "meter_id": item.meter_id,
                    "customer_id": item.customer_id,
                    "day": item.day,
                    "total_kwh": item.total_kwh,
                    "reading_count": item.reading_count,
                    "calculated_at": now,
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
            db.commit()

        return AggregateDailyJobResult(
            status="completed",
            readings_processed=len(readings),
            days_aggregated=len(daily_rows),
        )
