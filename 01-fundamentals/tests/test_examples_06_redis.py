from fastapi.testclient import TestClient

class MemoryRedis:
    """Very small stand-in for unit tests; real Redis is used when running the app."""
    def __init__(self):
        self.data = {}
        self.last_ttl = None
    def get(self, key):
        return self.data.get(key)
    def setex(self, key, ttl, value):
        self.last_ttl = ttl
        self.data[key] = value
    def delete(self, key):
        self.data.pop(key, None)

def test_cache_miss_hit_and_invalidation(load_example):
    module = load_example("06-redis-caching")
    cache = MemoryRedis()
    with TestClient(module.create_app(cache)) as api:
        first = api.get("/products/1")
        assert first.status_code == 200
        assert first.json()["cache_hit"] is False
        assert api.get("/products/1").json()["cache_hit"] is True
        assert cache.last_ttl == 60
        updated = api.put("/products/1", json={"name": "Keyboard Pro", "price_cents": 320000})
        assert updated.status_code == 200
        assert cache.get("demo:product:1") is None
        after = api.get("/products/1").json()
        assert after["cache_hit"] is False
        assert after["product"]["name"] == "Keyboard Pro"
        assert api.get("/products/404").status_code == 404
        assert api.put("/products/404", json={"name": "A", "price_cents": 1}).status_code == 404
