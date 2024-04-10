"""A cache-aside example using Redis, with dependency injection for tests."""
import json
import os
from typing import Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

class ProductInput(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    price_cents: int = Field(gt=0)

def create_app(cache: Any = None) -> FastAPI:
    api = FastAPI(title="Redis Cache Example")
    class RedisAdapter:
        """Connects only when a request needs Redis (handy for importing the app)."""
        def __init__(self):
            self._client = None
        def client(self):
            if self._client is None:
                import redis
                self._client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)
            return self._client
        def get(self, key):
            return self.client().get(key)
        def setex(self, key, ttl, value):
            return self.client().setex(key, ttl, value)
        def delete(self, key):
            return self.client().delete(key)
    cache_client = cache if cache is not None else RedisAdapter()
    products: dict[int, dict] = {1: {"id": 1, "name": "Mechanical keyboard", "price_cents": 299900}}
    api.state.cache = cache_client

    @api.get("/products/{product_id}")
    def product_detail(product_id: int):
        key = f"demo:product:{product_id}"
        try:
            stored = cache_client.get(key)
        except Exception:
            raise HTTPException(503, "Redis is unavailable") from None
        if stored:
            return {"product": json.loads(stored), "cache_hit": True}
        product = products.get(product_id)
        if not product:
            raise HTTPException(404, "Product not found")
        try:
            cache_client.setex(key, 60, json.dumps(product))
        except Exception:
            raise HTTPException(503, "Redis is unavailable") from None
        return {"product": product, "cache_hit": False}

    @api.put("/products/{product_id}")
    def update_product(product_id: int, payload: ProductInput):
        if product_id not in products:
            raise HTTPException(404, "Product not found")
        updated = {"id": product_id, **payload.model_dump()}
        products[product_id] = updated
        try:
            cache_client.delete(f"demo:product:{product_id}")
        except Exception:
            raise HTTPException(503, "Redis is unavailable") from None
        return updated

    return api

app = create_app()
