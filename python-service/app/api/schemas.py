from datetime import date, datetime

from pydantic import AwareDatetime, BaseModel, Field

from app.domain.models import ReadingQuality


class ReadingCreate(BaseModel):
    meter_id: str
    customer_id: str
    timestamp: AwareDatetime
    kwh: float = Field(ge=0)
    source: str
    quality: ReadingQuality
    external_id: str | None = None


class ReadingIngestResult(BaseModel):
    status: str
    reading_id: int


class AggregateDailyJobResult(BaseModel):
    status: str
    readings_processed: int
    days_aggregated: int


class DailyConsumptionRow(BaseModel):
    meter_id: str
    customer_id: str
    day: date
    total_kwh: float
    reading_count: int
    calculated_at: datetime
