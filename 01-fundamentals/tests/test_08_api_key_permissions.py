from fastapi.testclient import TestClient


def configured_client(load_tutorial):
    module = load_tutorial("08-api-key-permissions")
    return TestClient(module.create_app(read_key="reader-long-secret", admin_key="admin-long-secret"))


def test_missing_configuration_is_503(load_tutorial, monkeypatch):
    monkeypatch.delenv("DEMO_READ_KEY", raising=False)
    monkeypatch.delenv("DEMO_ADMIN_KEY", raising=False)
    client = TestClient(load_tutorial("08-api-key-permissions").create_app())
    assert client.get("/memos").status_code == 503


def test_missing_key_is_401(load_tutorial):
    assert configured_client(load_tutorial).get("/memos").status_code == 401


def test_wrong_key_is_401(load_tutorial):
    client = configured_client(load_tutorial)
    assert client.get("/memos", headers={"X-API-Key": "incorrect"}).status_code == 401


def test_reader_can_read_not_write(load_tutorial):
    client = configured_client(load_tutorial)
    headers = {"X-API-Key": "reader-long-secret"}
    assert client.get("/memos", headers=headers).status_code == 200
    assert client.post("/memos", headers=headers, json={"text": "hello"}).status_code == 403


def test_admin_can_write_and_read(load_tutorial):
    client = configured_client(load_tutorial)
    headers = {"X-API-Key": "admin-long-secret"}
    created = client.post("/memos", headers=headers, json={"text": "Write tests"})
    assert created.status_code == 201
    assert client.get("/memos", headers=headers).json()["items"] == ["Write tests"]


def test_empty_memo_is_rejected(load_tutorial):
    client = configured_client(load_tutorial)
    assert client.post("/memos", headers={"X-API-Key": "admin-long-secret"}, json={"text": ""}).status_code == 422
