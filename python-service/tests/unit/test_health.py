from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.api.routes import health as health_routes
from app.main import app


def test_health_reports_database_down_instead_of_500(monkeypatch) -> None:
    class FailingSession:
        def execute(self, statement):
            raise OperationalError("SELECT 1", {}, Exception("db down"))

        def close(self):
            return None

    monkeypatch.setattr(health_routes, "SessionLocal", lambda: FailingSession())

    with TestClient(app) as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"service": "up", "database": "down"}
