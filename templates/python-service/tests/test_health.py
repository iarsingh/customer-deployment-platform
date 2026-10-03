from fastapi.testclient import TestClient

from app.main import app


def test_health_names_the_service():
    client = TestClient(app)
    health = client.get("/healthz")
    ready = client.get("/readyz")
    assert health.status_code == 200
    assert health.json()["service"] == "__SERVICE_NAME__"
    assert ready.json()["status"] == "ready"
    assert ready.json()["environment"] == "__ENVIRONMENT__"
