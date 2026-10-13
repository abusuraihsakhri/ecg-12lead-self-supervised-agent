"""FastAPI service smoke and privacy-error tests."""
from fastapi.testclient import TestClient

from agents.api import app


def test_health_and_html_interface():
    client = TestClient(app)
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "HEALTHY"
    page = client.get("/")
    assert page.status_code == 200
    assert "12-Lead ECG Reference Tools" in page.text
    assert "DOSSIER-SIM" not in page.text


def test_audit_and_live_metrics():
    client = TestClient(app)
    before = client.get("/metrics").json()["dossiers_processed_total"]
    response = client.post("/api/audit", json={
        "task_id": "API-DEMO-1",
        "target_identifier": "KEY-1",
        "primary_metric": 10.0,
        "secondary_metric": 1.0,
        "status_descriptor": "NOMINAL",
        "is_critical_flag": False,
    })
    assert response.status_code == 200
    assert response.json()["overall_urgency"] == "ROUTINE"
    assert client.get("/metrics").json()["dossiers_processed_total"] == before + 1


def test_phi_guard_is_safe_http_error():
    client = TestClient(app)
    response = client.post("/api/audit", json={
        "task_id": "API-DEMO-2",
        "target_identifier": "MRN-987654",
        "primary_metric": 10.0,
        "secondary_metric": 1.0,
    })
    assert response.status_code == 422
    assert "sensitive" in response.json()["detail"]
    assert "987654" not in response.text
