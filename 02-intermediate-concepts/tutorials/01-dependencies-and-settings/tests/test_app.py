from fastapi.testclient import TestClient
from app import app, get_settings, Settings

def cfg():
    return Settings(application_name='Test', api_key='abc123', tax_percent=10)

def setup_function():
    app.dependency_overrides[get_settings] = cfg

def teardown_function():
    app.dependency_overrides.clear()

def test_health():
    assert TestClient(app).get('/health').json() == {'status': 'ok', 'service': 'Test'}

def test_requires_key():
    assert TestClient(app).post('/quotes', json={'description':'Book','unit_price_paise':1000,'units':2}).status_code == 401

def test_quote_calculation():
    r = TestClient(app).post('/quotes', headers={'x-api-key':'abc123'}, json={'description':'Book','unit_price_paise':1001,'units':2})
    assert r.status_code == 200
    assert r.json()['total_paise'] == 2202

def test_negative_price_rejected():
    r = TestClient(app).post('/quotes', headers={'x-api-key':'abc123'}, json={'description':'Book','unit_price_paise':-1,'units':2})
    assert r.status_code == 422
