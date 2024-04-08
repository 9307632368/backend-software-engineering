from fastapi.testclient import TestClient

def test_logging_and_configuration(load_example):
    module = load_example("07-logging-configuration")
    with TestClient(module.create_app(module.Settings("test", 1))) as api:
        response = api.get("/health")
        assert response.json() == {"status": "ok", "environment": "test"}
        assert len(response.headers["X-Request-ID"]) == 32
        assert api.post("/items", json={"name": "First"}).status_code == 201
        assert api.post("/items", json={"name": "Second"}).status_code == 409
        assert api.get("/items").json()["count"] == 1
        assert api.get("/items?limit=0").status_code == 422

def test_settings_from_environment(load_example, monkeypatch):
    module = load_example("07-logging-configuration")
    monkeypatch.setenv("MAX_ITEMS", "5")
    monkeypatch.setenv("APP_ENV", "local")
    assert module.Settings.from_env() == module.Settings("local", 5)
