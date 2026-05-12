from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models import DailyConsumption


class AnalyticsService:
    def get_meter_daily_consumption(self, db: Session, meter_id: str) -> list[DailyConsumption]:
        return list(
            db.scalars(
                select(DailyConsumption)
                .where(DailyConsumption.meter_id == meter_id)
                .order_by(DailyConsumption.day.asc())
            ).all()
        )

    def get_customer_daily_consumption(self, db: Session, customer_id: str) -> list[DailyConsumption]:
        return list(
            db.scalars(
                select(DailyConsumption)
                .where(DailyConsumption.customer_id == customer_id)
                .order_by(DailyConsumption.day.asc(), DailyConsumption.meter_id.asc())
            ).all()
        )
