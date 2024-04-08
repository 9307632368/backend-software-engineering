from fastapi.testclient import TestClient


def test_stock_returns_quantity(load_tutorial):
    client = TestClient(load_tutorial("03-error-handling").app)
    assert client.get("/stock/mouse").json() == {"sku": "mouse", "available": 12}


def test_unknown_sku_returns_404(load_tutorial):
    client = TestClient(load_tutorial("03-error-handling").app)
    assert client.get("/stock/unknown").status_code == 404
    assert client.post("/reservations/check", json={"sku": "unknown", "quantity": 1}).status_code == 404


def test_out_of_stock_returns_conflict(load_tutorial):
    client = TestClient(load_tutorial("03-error-handling").app)
    assert client.post("/reservations/check", json={"sku": "monitor", "quantity": 1}).status_code == 409


def test_too_many_items_reports_available(load_tutorial):
    client = TestClient(load_tutorial("03-error-handling").app)
    response = client.post("/reservations/check", json={"sku": "keyboard", "quantity": 6})
    assert response.status_code == 409
    assert response.json()["detail"]["available"] == 4


def test_valid_quantity_and_invalid_quantity(load_tutorial):
    client = TestClient(load_tutorial("03-error-handling").app)
    assert client.post("/reservations/check", json={"sku": "keyboard", "quantity": 2}).json()["can_reserve"]
    assert client.post("/reservations/check", json={"sku": "keyboard", "quantity": -1}).status_code == 422
