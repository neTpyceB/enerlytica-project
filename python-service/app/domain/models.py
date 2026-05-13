from datetime import date, datetime
from enum import Enum
from typing import Any

from sqlalchemy import CheckConstraint, Date, DateTime, Enum as SQLEnum, Float, Index, Integer, String, Text, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ReadingQuality(str, Enum):
    MEASURED = "measured"
    ESTIMATED = "estimated"
    CORRECTED = "corrected"


class RawReading(Base):
    __tablename__ = "raw_readings"
    __table_args__ = (
        CheckConstraint("kwh >= 0", name="ck_raw_readings_kwh_non_negative"),
        Index(
            "uq_raw_readings_meter_timestamp_when_external_id_null",
            "meter_id",
            "timestamp",
            unique=True,
            postgresql_where=text("external_id IS NULL"),
        ),
        Index(
            "uq_raw_readings_external_id_not_null",
            "external_id",
            unique=True,
            postgresql_where=text("external_id IS NOT NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    meter_id: Mapped[str] = mapped_column(String(128), nullable=False)
    customer_id: Mapped[str] = mapped_column(String(128), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    kwh: Mapped[float] = mapped_column(Float, nullable=False)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    quality: Mapped[ReadingQuality] = mapped_column(
        SQLEnum(
            ReadingQuality,
            name="reading_quality",
            values_callable=lambda enum_class: [member.value for member in enum_class],
        ),
        nullable=False,
    )
    external_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class RejectedReading(Base):
    __tablename__ = "rejected_readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    raw_payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class DailyConsumption(Base):
    __tablename__ = "daily_consumption"
    __table_args__ = (UniqueConstraint("meter_id", "day", name="uq_daily_consumption_meter_day"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    meter_id: Mapped[str] = mapped_column(String(128), nullable=False)
    customer_id: Mapped[str] = mapped_column(String(128), nullable=False)
    day: Mapped[date] = mapped_column(Date, nullable=False)
    total_kwh: Mapped[float] = mapped_column(Float, nullable=False)
    reading_count: Mapped[int] = mapped_column(Integer, nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class DataQualityIssue(Base):
    __tablename__ = "data_quality_issues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    meter_id: Mapped[str] = mapped_column(String(128), nullable=False)
    issue_type: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class JobRun(Base):
    __tablename__ = "job_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_name: Mapped[str] = mapped_column(String(128), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    records_processed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_failed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
