from fastapi.testclient import TestClient
from app import FakeSupplier, create_app

def test_happy_path():
    assert TestClient(create_app()).get('/quotes/ABC').json() == {'sku':'ABC','price_cents':2499}

def test_one_retry_succeeds():
    supplier = FakeSupplier(failures_left=1)
    c = TestClient(create_app(supplier=supplier))
    assert c.get('/quotes/A').status_code == 200
    assert supplier.calls == 2

def test_circuit_opens_then_recovers():
    clock = [100.0]
    supplier = FakeSupplier(failures_left=20)
    c = TestClient(create_app(supplier=supplier, clock=lambda: clock[0], threshold=2, cooldown=10))
    assert c.get('/quotes/A').status_code == 503
    assert c.get('/quotes/A').status_code == 503
    calls = supplier.calls
    assert c.get('/quotes/A').status_code == 503
    assert supplier.calls == calls  # fail fast; supplier not called
    assert c.get('/health/supplier').json()['circuit'] == 'open'
    clock[0] += 11
    supplier.failures_left = 0
    assert c.get('/quotes/A').status_code == 200
    assert c.get('/health/supplier').json()['circuit'] == 'closed'
