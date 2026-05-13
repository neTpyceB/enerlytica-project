from datetime import date, datetime, timezone
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.routes import analytics as analytics_routes
from app.api.routes import jobs as jobs_routes
from app.api.routes import readings as readings_routes
from app.domain.errors import DomainValidationError
from app.infrastructure.database import get_db
from app.main import app


def _override_get_db():
    yield SimpleNamespace()


def test_readings_api_flow_with_duplicate_and_rejection(monkeypatch) -> None:
    class FakeIngestionService:
        def ingest(self, db, payload):
            if payload.meter_id == "BAD":
                raise DomainValidationError("meter_id is required")
            if payload.external_id == "dup-id":
                return SimpleNamespace(status="duplicate", reading_id=7)
            return SimpleNamespace(status="accepted", reading_id=6)

    monkeypatch.setattr(readings_routes, "ingestion_service", FakeIngestionService())
    app.dependency_overrides[get_db] = _override_get_db

    with TestClient(app) as client:
        accepted = client.post(
            "/api/readings",
            json={
                "meter_id": "METER-001",
                "customer_id": "CUSTOMER-001",
                "timestamp": "2026-05-01T10:00:00+00:00",
                "kwh": 1.0,
                "source": "legacy_php",
                "quality": "measured",
            },
        )
        duplicate = client.post(
            "/api/readings",
            json={
                "meter_id": "METER-001",
                "customer_id": "CUSTOMER-001",
                "timestamp": "2026-05-01T10:00:00+00:00",
                "kwh": 1.0,
                "source": "legacy_php",
                "quality": "measured",
                "external_id": "dup-id",
            },
        )
        rejected = client.post(
            "/api/readings",
            json={
                "meter_id": "BAD",
                "customer_id": "CUSTOMER-001",
                "timestamp": "2026-05-01T10:00:00+00:00",
                "kwh": 1.0,
                "source": "legacy_php",
                "quality": "measured",
            },
        )

    app.dependency_overrides.clear()

    assert accepted.status_code == 200
    assert accepted.json() == {"status": "accepted", "reading_id": 6}
    assert duplicate.status_code == 200
    assert duplicate.json() == {"status": "duplicate", "reading_id": 7}
    assert rejected.status_code == 422
    assert rejected.json()["detail"] == "meter_id is required"


def test_jobs_api_flow(monkeypatch) -> None:
    now = datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)

    class FakeJobService:
        def aggregate_daily_consumption(self, db):
            return SimpleNamespace(status="completed", readings_processed=5, days_aggregated=2)

        def list_job_runs(self, db):
            return [
                SimpleNamespace(
                    id=1,
                    job_name="aggregate_daily_consumption",
                    started_at=now,
                    finished_at=now,
                    status="completed",
                    records_processed=5,
                    records_failed=0,
                    message="ok",
                )
            ]

    monkeypatch.setattr(jobs_routes, "job_service", FakeJobService())
    app.dependency_overrides[get_db] = _override_get_db

    with TestClient(app) as client:
        aggregate = client.post("/api/jobs/aggregate-daily")
        runs = client.get("/api/jobs")

    app.dependency_overrides.clear()

    assert aggregate.status_code == 200
    assert aggregate.json() == {
        "status": "completed",
        "readings_processed": 5,
        "days_aggregated": 2,
    }
    assert runs.status_code == 200
    assert runs.json()[0]["job_name"] == "aggregate_daily_consumption"
    assert runs.json()[0]["status"] == "completed"


def test_analytics_api_flow(monkeypatch) -> None:
    now = datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)

    class FakeAnalyticsService:
        def get_meter_daily_consumption(self, db, meter_id):
            return [
                SimpleNamespace(
                    meter_id=meter_id,
                    customer_id="CUSTOMER-001",
                    day=date(2026, 5, 1),
                    total_kwh=3.2,
                    reading_count=3,
                    calculated_at=now,
                )
            ]

        def get_customer_daily_consumption(self, db, customer_id):
            return [
                SimpleNamespace(
                    meter_id="METER-001",
                    customer_id=customer_id,
                    day=date(2026, 5, 1),
                    total_kwh=3.2,
                    reading_count=3,
                    calculated_at=now,
                )
            ]

    monkeypatch.setattr(analytics_routes, "analytics_service", FakeAnalyticsService())
    app.dependency_overrides[get_db] = _override_get_db

    with TestClient(app) as client:
        meter = client.get("/api/meters/METER-001/daily-consumption")
        customer = client.get("/api/customers/CUSTOMER-001/daily-consumption")

    app.dependency_overrides.clear()

    assert meter.status_code == 200
    assert meter.json()[0]["meter_id"] == "METER-001"
    assert meter.json()[0]["total_kwh"] == 3.2
    assert customer.status_code == 200
    assert customer.json()[0]["customer_id"] == "CUSTOMER-001"
