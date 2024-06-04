from fastapi.testclient import TestClient
from app import create_app

def test_bucket_limits_burst_and_refills():
    clock=[0.0]
    c = TestClient(create_app(clock=lambda:clock[0],capacity=2,refill_per_second=0.5))
    h={'X-API-Key':'demo-alpha'}
    assert c.get('/reports',headers=h).status_code == 200
    assert c.get('/reports',headers=h).status_code == 200
    r = c.get('/reports',headers=h)
    assert r.status_code == 429 and r.headers['Retry-After'] == '2'
    clock[0] += 2
    assert c.get('/reports',headers=h).status_code == 200

def test_buckets_independent_and_keys_required():
    c = TestClient(create_app(capacity=1))
    assert c.get('/reports').status_code == 401
    assert c.get('/reports', headers={'X-API-Key':'demo-alpha'}).status_code == 200
    assert c.get('/reports', headers={'X-API-Key':'demo-alpha'}).status_code == 429
    assert c.get('/reports', headers={'X-API-Key':'demo-beta'}).status_code == 200
