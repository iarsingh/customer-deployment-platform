from fastapi.testclient import TestClient

from app.main import create_app


def client_for(tmp_path):
    return TestClient(create_app(data_dir=tmp_path))


def test_accepts_a_dev_python_service(tmp_path):
    client = client_for(tmp_path)
    response = client.post(
        "/services",
        json={
            "name": "billing-callback",
            "team": "payments",
            "runtime": "python",
            "environment": "dev",
            "idempotency_key": "evt-1",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "accepted"
    assert body["refusals"] == []
    assert body["id"].startswith("svc-")


def test_prod_is_refused_and_stored(tmp_path):
    client = client_for(tmp_path)
    response = client.post(
        "/services",
        json={
            "name": "billing-callback",
            "team": "payments",
            "runtime": "python",
            "environment": "prod",
            "idempotency_key": "evt-prod",
        },
    )
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["status"] == "refused"
    assert any("prod" in reason for reason in detail["refusals"])
    listed = client.get("/services").json()["services"]
    assert listed[0]["id"] == detail["id"]


def test_unknown_runtime_is_refused(tmp_path):
    client = client_for(tmp_path)
    response = client.post(
        "/services",
        json={"name": "billing-callback", "team": "payments", "runtime": "go", "environment": "dev"},
    )
    assert response.status_code == 422
    assert any("python" in reason for reason in response.json()["detail"]["refusals"])


def test_bad_name_is_refused(tmp_path):
    client = client_for(tmp_path)
    response = client.post(
        "/services",
        json={"name": "Billing_API", "team": "payments", "runtime": "python", "environment": "dev"},
    )
    assert response.status_code == 422


def test_same_idempotency_key_returns_the_original(tmp_path):
    client = client_for(tmp_path)
    payload = {
        "name": "billing-callback",
        "team": "payments",
        "runtime": "python",
        "environment": "staging",
        "idempotency_key": "evt-1",
    }
    first = client.post("/services", json=payload).json()
    second = client.post("/services", json=payload).json()
    assert second["id"] == first["id"]
    assert len(client.get("/services").json()["services"]) == 1


def test_accepted_request_renders_a_repository(tmp_path):
    client = client_for(tmp_path)
    body = client.post(
        "/services",
        json={
            "name": "billing-callback",
            "team": "payments",
            "runtime": "python",
            "environment": "dev",
            "idempotency_key": "render-1",
        },
    ).json()
    repository = tmp_path / body["artifacts"]["repository"]
    source = (repository / "app" / "main.py").read_text()
    dockerfile = (repository / "Dockerfile").read_text()
    values = (tmp_path / body["artifacts"]["helm_values"]).read_text()
    assert 'service": "billing-callback"' in source or '"service": "billing-callback"' in source
    assert "__SERVICE_NAME__" not in source
    assert ":latest" not in dockerfile
    assert 'tag: "0.1.0"' in values
    assert (tmp_path / body["artifacts"]["gitops_application"]).exists()


def test_metrics_count_decisions(tmp_path):
    client = client_for(tmp_path)
    client.post(
        "/services",
        json={"name": "billing-callback", "team": "payments", "runtime": "python", "environment": "dev"},
    )
    client.post(
        "/services",
        json={"name": "billing-callback", "team": "payments", "runtime": "python", "environment": "prod"},
    )
    body = client.get("/metrics").text
    assert 'meridian_service_requests_total{status="accepted"} 1' in body
    assert 'meridian_service_requests_total{status="refused"} 1' in body


def test_unknown_id_is_404(tmp_path):
    client = client_for(tmp_path)
    assert client.get("/services/svc-missing").status_code == 404
    assert client.get("/healthz").json()["status"] == "ok"
