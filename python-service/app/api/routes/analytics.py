from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas import DailyConsumptionRow
from app.application.analytics_service import AnalyticsService
from app.infrastructure.database import get_db


router = APIRouter(prefix="/api", tags=["analytics"])
analytics_service = AnalyticsService()


@router.get("/meters/{meter_id}/daily-consumption", response_model=list[DailyConsumptionRow])
def get_meter_daily_consumption(meter_id: str, db: Session = Depends(get_db)) -> list[DailyConsumptionRow]:
    rows = analytics_service.get_meter_daily_consumption(db, meter_id)
    return [DailyConsumptionRow.model_validate(row, from_attributes=True) for row in rows]


@router.get("/customers/{customer_id}/daily-consumption", response_model=list[DailyConsumptionRow])
def get_customer_daily_consumption(customer_id: str, db: Session = Depends(get_db)) -> list[DailyConsumptionRow]:
    rows = analytics_service.get_customer_daily_consumption(db, customer_id)
    return [DailyConsumptionRow.model_validate(row, from_attributes=True) for row in rows]
