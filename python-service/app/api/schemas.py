from datetime import date, datetime

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from app.domain.models import ReadingQuality


class ReadingCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    meter_id: str = Field(min_length=1, max_length=128)
    customer_id: str = Field(min_length=1, max_length=128)
    timestamp: AwareDatetime
    kwh: float = Field(ge=0, allow_inf_nan=False)
    source: str = Field(min_length=1, max_length=64)
    quality: ReadingQuality
    external_id: str | None = Field(default=None, max_length=128)


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
