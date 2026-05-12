"""Initial schema for Enerlytica modernization demo.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-12 22:45:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


reading_quality = postgresql.ENUM(
    "measured",
    "estimated",
    "corrected",
    name="reading_quality",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    reading_quality.create(bind, checkfirst=True)

    op.create_table(
        "raw_readings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("meter_id", sa.String(length=128), nullable=False),
        sa.Column("customer_id", sa.String(length=128), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("kwh", sa.Float(), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("quality", reading_quality, nullable=False),
        sa.Column("external_id", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("kwh >= 0", name="ck_raw_readings_kwh_non_negative"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("meter_id", "timestamp", name="uq_raw_readings_meter_timestamp"),
    )
    op.create_index(
        "uq_raw_readings_external_id_not_null",
        "raw_readings",
        ["external_id"],
        unique=True,
        postgresql_where=sa.text("external_id IS NOT NULL"),
    )

    op.create_table(
        "rejected_readings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("raw_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "daily_consumption",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("meter_id", sa.String(length=128), nullable=False),
        sa.Column("customer_id", sa.String(length=128), nullable=False),
        sa.Column("day", sa.Date(), nullable=False),
        sa.Column("total_kwh", sa.Float(), nullable=False),
        sa.Column("reading_count", sa.Integer(), nullable=False),
        sa.Column("calculated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("meter_id", "day", name="uq_daily_consumption_meter_day"),
    )

    op.create_table(
        "data_quality_issues",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("meter_id", sa.String(length=128), nullable=False),
        sa.Column("issue_type", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "job_runs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("job_name", sa.String(length=128), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("records_processed", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("records_failed", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("job_runs")
    op.drop_table("data_quality_issues")
    op.drop_table("daily_consumption")
    op.drop_table("rejected_readings")
    op.drop_index("uq_raw_readings_external_id_not_null", table_name="raw_readings")
    op.drop_table("raw_readings")

    bind = op.get_bind()
    reading_quality.drop(bind, checkfirst=True)
