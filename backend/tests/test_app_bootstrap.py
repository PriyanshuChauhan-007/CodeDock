from fastapi.testclient import TestClient

from app.main import create_app


def test_live_health_endpoint() -> None:
    client = TestClient(create_app())

    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_health_endpoint_reports_application_check() -> None:
    client = TestClient(create_app())

    response = client.get("/health/ready")

    assert response.status_code in {200, 503}
    assert response.json()["checks"]["application"] == "ok"
    assert "postgres" in response.json()["checks"]
