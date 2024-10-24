from concurrent.futures import ThreadPoolExecutor
import pytest
from fastapi.testclient import TestClient
from flash_sale.app import create_app
from flash_sale.store import FlashSaleStore, StoreError

@pytest.fixture
def system(tmp_path):
    app = create_app(tmp_path / "shop.sqlite3")
    app.state.store.add_product("SKU-1", "Demo Phone", 5, 7500)
    return TestClient(app), app.state.store


def post(client, client_id="student1", key="request-0001", sku="SKU-1", qty=2):
    return client.post("/orders", json={"client_id":client_id,"sku":sku,"quantity":qty},
                       headers={"Idempotency-Key":key})


def test_order_and_stock(system):
    client, _ = system
    result = post(client)
    assert result.status_code == 201
    assert result.json()["total_cents"] == 15000
    assert client.get("/products/SKU-1").json()["stock"] == 3
    assert client.get("/orders/" + result.json()["order_id"]).status_code == 200


def test_idempotency_replay(system):
    client, _ = system
    first = post(client)
    second = post(client)
    assert second.status_code == 200
    assert second.headers["Idempotency-Replayed"] == "true"
    assert first.json() == second.json()
    assert client.get("/products/SKU-1").json()["stock"] == 3


def test_reusing_same_key_with_different_request_rejected(system):
    client, _ = system
    assert post(client, qty=1).status_code == 201
    assert post(client, qty=3).status_code == 409
    assert client.get("/products/SKU-1").json()["stock"] == 4


def test_insufficient_stock_no_partial_debit(system):
    client, _ = system
    assert post(client, qty=6).status_code == 409
    assert client.get("/products/SKU-1").json()["stock"] == 5


def test_missing_sku(system):
    client, _ = system
    assert post(client, sku="MISSING").status_code == 404
    assert client.get("/orders/not-here").status_code == 404


def test_validation_requires_idempotency_key(system):
    client, _ = system
    assert client.post("/orders", json={"client_id":"test", "sku":"SKU-1", "quantity":1}).status_code == 422
    assert post(client, qty=0).status_code == 422


def test_parallel_buyers_do_not_oversell(system):
    _, store = system
    def buy(number):
        try:
            store.place_order(f"buyer{number}", f"order-{number}", "SKU-1", 1)
            return "ok"
        except StoreError as e:
            return e.status_code
    with ThreadPoolExecutor(max_workers=12) as pool:
        results = list(pool.map(buy, range(12)))
    assert results.count("ok") == 5
    assert results.count(409) == 7
    assert store.get_product("SKU-1")["stock"] == 0


def test_persistence_across_store_instances(tmp_path):
    path=tmp_path / "persist.sqlite3"
    first=FlashSaleStore(path)
    first.add_product("A", "Gadget", 2, 100)
    first.place_order("c1", "request1", "A", 1)
    assert FlashSaleStore(path).get_product("A")["stock"] == 1
