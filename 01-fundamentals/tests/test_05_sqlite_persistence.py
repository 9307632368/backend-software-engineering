from fastapi.testclient import TestClient
import sqlite3


def test_ticket_flow(load_tutorial, tmp_path):
    module = load_tutorial("05-sqlite-persistence")
    with TestClient(module.create_app(tmp_path / "tickets.db")) as client:
        created = client.post("/tickets", json={"subject": "Login error", "priority": "high"})
        assert created.status_code == 201
        ticket_id = created.json()["id"]
        assert created.json()["status"] == "open"
        assert client.get(f"/tickets/{ticket_id}").status_code == 200
        assert len(client.get("/tickets").json()) == 1
        assert client.patch(f"/tickets/{ticket_id}/close").json()["status"] == "closed"
        assert client.patch(f"/tickets/{ticket_id}/close").status_code == 409
        assert client.delete(f"/tickets/{ticket_id}").status_code == 204
        assert client.get(f"/tickets/{ticket_id}").status_code == 404


def test_data_survives_new_app_instance(load_tutorial, tmp_path):
    module = load_tutorial("05-sqlite-persistence")
    path = tmp_path / "persist.db"
    with TestClient(module.create_app(path)) as client:
        client.post("/tickets", json={"subject": "Disk usage alert", "priority": "low"})
    with TestClient(module.create_app(path)) as client:
        result = client.get("/tickets").json()
        assert len(result) == 1
        assert result[0]["subject"] == "Disk usage alert"


def test_invalid_priority_and_limit(load_tutorial, tmp_path):
    module = load_tutorial("05-sqlite-persistence")
    with TestClient(module.create_app(tmp_path / "validation.db")) as client:
        assert client.post("/tickets", json={"subject": "System error", "priority": "urgent"}).status_code == 422
        assert client.get("/tickets?limit=0").status_code == 422


def test_unknown_ticket_returns_404(load_tutorial, tmp_path):
    module = load_tutorial("05-sqlite-persistence")
    with TestClient(module.create_app(tmp_path / "missing.db")) as client:
        assert client.get("/tickets/991").status_code == 404
        assert client.patch("/tickets/991/close").status_code == 404
        assert client.delete("/tickets/991").status_code == 404


def test_sql_injection_string_is_treated_as_data(load_tutorial, tmp_path):
    module = load_tutorial("05-sqlite-persistence")
    with TestClient(module.create_app(tmp_path / "safe.db")) as client:
        subject = "Help'; DROP TABLE tickets; --"
        response = client.post("/tickets", json={"subject": subject, "priority": "medium"})
        assert response.status_code == 201
        assert response.json()["subject"] == subject
        assert client.get("/tickets").status_code == 200
