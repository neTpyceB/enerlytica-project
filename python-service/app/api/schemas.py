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


class JobRunRow(BaseModel):
    id: int
    job_name: str
    started_at: datetime
    finished_at: datetime | None
    status: str
    records_processed: int
    records_failed: int
    message: str | None


class DataQualityIssueRow(BaseModel):
    id: int
    meter_id: str
    issue_type: str
    description: str
    severity: str
    detected_at: datetime
