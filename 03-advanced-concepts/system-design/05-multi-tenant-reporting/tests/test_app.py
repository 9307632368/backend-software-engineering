from fastapi.testclient import TestClient
from app import create_app

def test_tenants_cannot_read_other_records(tmp_path):
    c = TestClient(create_app(tmp_path/'tenant.db'))
    red = {'X-API-Key':'demo-red-key'}
    blue = {'X-API-Key':'demo-blue-key'}
    assert c.post('/orders',headers=red,json={'amount_cents':1200}).status_code == 201
    assert c.post('/orders',headers=blue,json={'amount_cents':750}).status_code == 201
    assert c.get('/reports/sales',headers=red).json() == {'tenant_id':'red','orders':1,'total_cents':1200}
    assert c.get('/reports/sales',headers=blue).json()['total_cents'] == 750
    assert len(c.get('/orders',headers=blue).json()) == 1
    assert c.get('/orders',headers=blue).json()[0]['amount_cents'] == 750

def test_missing_or_invalid_credentials(tmp_path):
    c = TestClient(create_app(tmp_path/'tenant.db'))
    assert c.get('/reports/sales').status_code == 401
    assert c.post('/orders', headers={'X-API-Key':'bad'},json={'amount_cents':400}).status_code == 401
    assert c.post('/orders', headers={'X-API-Key':'demo-red-key'},json={'amount_cents':-1}).status_code == 422

def test_untrusted_tenant_header_does_not_switch_tenant(tmp_path):
    c = TestClient(create_app(tmp_path/'tenant.db'))
    headers = {'X-API-Key':'demo-red-key','X-Tenant-Id':'blue'}
    assert c.post('/orders', headers=headers,json={'amount_cents':500}).json()['tenant_id'] == 'red'
