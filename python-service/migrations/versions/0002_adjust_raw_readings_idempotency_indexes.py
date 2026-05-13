"""Adjust raw_readings idempotency indexes.

Revision ID: 0002_raw_readings_idempotency
Revises: 0001_initial_schema
Create Date: 2026-05-13 09:45:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0002_raw_readings_idempotency"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint(
        "uq_raw_readings_meter_timestamp",
        "raw_readings",
        type_="unique",
    )
    op.create_index(
        "uq_raw_readings_meter_timestamp_when_external_id_null",
        "raw_readings",
        ["meter_id", "timestamp"],
        unique=True,
        postgresql_where=sa.text("external_id IS NULL"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_raw_readings_meter_timestamp_when_external_id_null",
        table_name="raw_readings",
    )
    op.create_unique_constraint(
        "uq_raw_readings_meter_timestamp",
        "raw_readings",
        ["meter_id", "timestamp"],
    )
