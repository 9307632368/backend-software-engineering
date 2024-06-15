def make_product(client, admin, sku="SKU-101", stock=5, price=1250):
    r = client.post("/products", headers=admin, json={"sku": sku, "name": "Demo item", "stock": stock, "price_cents": price})
    assert r.status_code == 201, r.text
    return r.json()["id"]

def test_checkout_money_stock_cancel_and_audit(ctx, account):
    client, _ = ctx
    admin = account("admin@example.com", "admin")
    customer = account("a@example.com")
    pid = make_product(client, admin)
    h = {**customer, "Idempotency-Key": "order-key-001"}
    payload = {"items": [{"product_id": pid, "quantity": 2}]}
    order = client.post("/orders", json=payload, headers=h)
    assert order.status_code == 201, order.text
    assert order.json()["total_cents"] == 2500
    assert client.post("/orders", json=payload, headers=h).json()["id"] == order.json()["id"]
    assert client.get("/products").json()[0]["stock"] == 3
    oid = order.json()["id"]
    assert client.post(f"/orders/{oid}/cancel", headers=customer).status_code == 200
    assert client.get("/products").json()[0]["stock"] == 5
    assert client.post(f"/orders/{oid}/cancel", headers=customer).status_code == 409
    assert [x["event"] for x in client.get(f"/orders/{oid}/audit", headers=admin).json()] == ["placed", "cancelled"]

def test_atomic_rollback_on_second_item_shortage(ctx, account):
    client, _ = ctx
    admin = account("staff@example.com", "admin")
    customer = account("buyer@example.com")
    a = make_product(client, admin, "AA", 3)
    b = make_product(client, admin, "BB", 0)
    r = client.post("/orders", headers={**customer, "Idempotency-Key": "order-key-002"}, json={"items": [{"product_id": a, "quantity": 2}, {"product_id": b, "quantity": 1}]})
    assert r.status_code == 409
    assert [x["stock"] for x in client.get("/products").json()] == [3, 0]
    assert client.get("/orders", headers=customer).json() == []

def test_user_isolation_and_permissions(ctx, account):
    client, _ = ctx
    admin = account("admin2@example.com", "admin")
    a = account("first@example.com")
    b = account("second@example.com")
    pid = make_product(client, admin)
    assert client.post("/products", headers=a, json={"sku": "no", "name": "Secret", "price_cents": 20, "stock": 0}).status_code == 403
    response = client.post("/orders", headers={**a, "Idempotency-Key": "order-key-003"}, json={"items": [{"product_id": pid, "quantity": 1}]})
    oid = response.json()["id"]
    assert client.get(f"/orders/{oid}", headers=b).status_code == 404
    assert client.get("/orders", headers=b).json() == []
    assert client.post(f"/orders/{oid}/fulfill", headers=b).status_code == 403
    assert client.post(f"/orders/{oid}/fulfill", headers=admin).status_code == 200
    assert client.post(f"/orders/{oid}/cancel", headers=a).status_code == 409

def test_bad_inputs_and_auth(ctx, account):
    client, _ = ctx
    admin = account("p@example.com", "admin")
    assert client.post("/auth/register", json={"email": "new@example.com", "password": "password123", "role": "admin"}).status_code == 422
    assert client.post("/auth/register", json={"email": "new@example.com", "password": "password123"}).status_code == 201
    assert client.post("/auth/login", json={"email": "new@example.com", "password": "wrongpass123"}).status_code == 401
    assert client.get("/orders").status_code == 401
    assert client.post("/products", headers=admin, json={"sku": "bad", "name": "Item", "stock": -1, "price_cents": 0}).status_code == 422
    assert client.post("/products", headers=admin, json={"sku": "good", "name": "Item", "stock": 1, "price_cents": 30}).status_code == 201
    assert client.post("/products", headers=admin, json={"sku": "good", "name": "Item", "stock": 1, "price_cents": 30}).status_code == 409


def test_order_persistence_after_app_restart(ctx, account):
    client, app = ctx
    admin = account("persist-admin@example.com", "admin")
    buyer = account("persist-buyer@example.com")
    pid = make_product(client, admin, sku="SAVED", stock=4, price=215)
    response = client.post("/orders", headers={**buyer, "Idempotency-Key": "persist-key-001"}, json={"items": [{"product_id": pid, "quantity": 3}]})
    assert response.status_code == 201
    first_id = response.json()["id"]
    # Recreate application with same SQLite DB to prove the data was committed.
    from app.main import create_app
    fresh = create_app(str(app.state.engine.url), jwt_secret="a-test-secret-that-is-long-enough")
    from fastapi.testclient import TestClient
    with TestClient(fresh) as second_client:
        assert second_client.get("/orders", headers=buyer).json()[0]["id"] == first_id
        assert second_client.get("/products").json()[0]["stock"] == 1


def test_multi_item_snapshot_and_invalid_checkout(ctx, account):
    client, _ = ctx
    admin = account("item-admin@example.com", "admin")
    buyer = account("item-buyer@example.com")
    a = make_product(client, admin, "PRODUCT-A", 10, 199)
    b = make_product(client, admin, "PRODUCT-B", 10, 250)
    data = {"items": [{"product_id": a, "quantity": 3}, {"product_id": b, "quantity": 2}]}
    r = client.post("/orders", headers={**buyer,"Idempotency-Key": "multi-order-001"}, json=data)
    assert r.status_code == 201
    assert r.json()["total_cents"] == 1097
    assert len(r.json()["items"]) == 2
    dup = client.post("/orders", headers={**buyer,"Idempotency-Key": "multi-order-002"}, json={"items":[{"product_id": a, "quantity": 2},{"product_id": a,"quantity":2}]})
    assert dup.status_code == 422
    assert client.get("/products").json()[0]["stock"] == 7


def test_token_validation_and_admin_audit_scope(ctx, account):
    client, _ = ctx
    a = account("user-a@example.com")
    assert client.get("/orders", headers={"Authorization": "Bearer deliberatelyinvalid"}).status_code == 401
    assert client.get("/orders/999", headers=a).status_code == 404
    assert client.get("/orders/999/audit", headers=a).status_code == 403
