from fastapi.testclient import TestClient


def test_crud_flow(load_tutorial):
    module = load_tutorial("04-in-memory-crud")
    client = TestClient(module.create_app())
    created = client.post("/notes", json={"title": "Read API docs", "body": "Try examples"})
    assert created.status_code == 201
    assert created.json()["id"] == 1
    assert len(client.get("/notes").json()) == 1
    assert client.get("/notes/1").json()["title"] == "Read API docs"
    updated = client.patch("/notes/1", json={"title": "Read and test API"})
    assert updated.status_code == 200
    assert updated.json()["body"] == "Try examples"
    assert client.delete("/notes/1").status_code == 204
    assert client.get("/notes/1").status_code == 404


def test_deleted_twice_is_404(load_tutorial):
    client = TestClient(load_tutorial("04-in-memory-crud").create_app())
    client.post("/notes", json={"title": "A", "body": "B"})
    assert client.delete("/notes/1").status_code == 204
    assert client.delete("/notes/1").status_code == 404


def test_update_missing_note_is_404(load_tutorial):
    client = TestClient(load_tutorial("04-in-memory-crud").create_app())
    assert client.patch("/notes/100", json={"title": "Changed"}).status_code == 404


def test_null_update_is_rejected(load_tutorial):
    client = TestClient(load_tutorial("04-in-memory-crud").create_app())
    client.post("/notes", json={"title": "A", "body": "B"})
    assert client.patch("/notes/1", json={"title": None}).status_code == 422


def test_app_factory_has_separate_state(load_tutorial):
    module = load_tutorial("04-in-memory-crud")
    first = TestClient(module.create_app())
    second = TestClient(module.create_app())
    first.post("/notes", json={"title": "First", "body": "Only first"})
    assert second.get("/notes").json() == []
