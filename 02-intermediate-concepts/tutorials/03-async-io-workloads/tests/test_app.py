import asyncio
from fastapi.testclient import TestClient
import app as module

def test_parallel_io_results():
    r=TestClient(module.app).post('/availability',json={'sku':'BOOK-10'})
    assert r.status_code == 200
    assert r.json()=={'sku':'BOOK-10','stock':12,'delivery_days':3}

def test_timeout(monkeypatch):
    async def slow(sku):
        await asyncio.sleep(.03)
        return {'stock':0}
    monkeypatch.setattr(module,'get_stock',slow)
    r=TestClient(module.app).post('/availability',json={'sku':'BOOK-10','timeout_ms':1})
    assert r.status_code == 504

def test_validation():
    assert TestClient(module.app).post('/availability',json={'sku':'x'}).status_code == 422
