from app.domain.models import DailyConsumption, DataQualityIssue, JobRun, RawReading, RejectedReading
from app.main import app


def test_app_metadata() -> None:
    assert app.title == "Enerlytica Modernization Demo API"
    assert app.docs_url == "/docs"
    assert app.openapi_url == "/openapi.json"


def test_core_tables_declared() -> None:
    table_names = {table.name for table in RawReading.metadata.sorted_tables}

    assert "raw_readings" in table_names
    assert "rejected_readings" in table_names
    assert "daily_consumption" in table_names
    assert "data_quality_issues" in table_names
    assert "job_runs" in table_names

    assert RawReading.__tablename__ == "raw_readings"
    assert RejectedReading.__tablename__ == "rejected_readings"
    assert DailyConsumption.__tablename__ == "daily_consumption"
    assert DataQualityIssue.__tablename__ == "data_quality_issues"
    assert JobRun.__tablename__ == "job_runs"


def test_raw_reading_indexes_declared_for_partial_idempotency() -> None:
    index_names = {index.name for index in RawReading.__table__.indexes}

    assert "uq_raw_readings_external_id_not_null" in index_names
    assert "uq_raw_readings_meter_timestamp_when_external_id_null" in index_names
