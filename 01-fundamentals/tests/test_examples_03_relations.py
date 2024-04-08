from fastapi.testclient import TestClient

def make_client(tmp_path, load_example):
    module = load_example("03-database-relationships")
    return TestClient(module.create_app(f"sqlite:///{tmp_path / 'shop.db'}"))

def test_order_and_relationships(tmp_path, load_example):
    with make_client(tmp_path, load_example) as api:
        user = api.post("/users", json={"name": "Riya"}).json()
        product = api.post("/products", json={"name": "Notebook", "price_cents": 2750, "stock": 5}).json()
        order = api.post("/orders", json={"user_id": user["id"], "product_id": product["id"], "quantity": 2})
        assert order.status_code == 201
        assert order.json()["total_cents"] == 5500
        items = api.get(f"/users/{user['id']}/orders").json()
        assert len(items) == 1
        assert items[0]["lines"][0]["quantity"] == 2
        assert api.post("/orders", json={"user_id": user["id"], "product_id": product["id"], "quantity": 4}).status_code == 409
        assert api.post("/products", json={"name": "Notebook", "price_cents": 2750, "stock": 1}).status_code == 409

def test_relations_persist_after_restart(tmp_path, load_example):
    with make_client(tmp_path, load_example) as api:
        user = api.post("/users", json={"name": "Amol"}).json()
        product = api.post("/products", json={"name": "Pen", "price_cents": 120, "stock": 8}).json()
        api.post("/orders", json={"user_id": user["id"], "product_id": product["id"], "quantity": 1})
    with make_client(tmp_path, load_example) as api:
        assert len(api.get(f"/users/{user['id']}/orders").json()) == 1
        assert api.post("/orders", json={"user_id": 999, "product_id": product["id"], "quantity": 1}).status_code == 404
        assert api.post("/orders", json={"user_id": user["id"], "product_id": 999, "quantity": 1}).status_code == 404
