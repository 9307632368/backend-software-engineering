from fastapi.testclient import TestClient
from app import create_app

def test_version_update_and_stale_conflict(tmp_path):
    c = TestClient(create_app(tmp_path / 'stock.db'))
    initial = c.get('/products/1').json()
    assert initial['version'] == 1
    r = c.patch('/products/1/stock', json={'expected_version':1, 'delta':-4})
    assert (r.status_code, r.json()['stock'], r.json()['version']) == (200, 6, 2)
    assert c.patch('/products/1/stock', json={'expected_version':1, 'delta':-2}).status_code == 409
    assert c.get('/products/1').json()['stock'] == 6

def test_stock_floor_missing_and_validation(tmp_path):
    c = TestClient(create_app(tmp_path / 'stock.db'))
    assert c.patch('/products/1/stock', json={'expected_version':1,'delta':-15}).status_code == 422
    assert c.patch('/products/77/stock', json={'expected_version':1,'delta':-1}).status_code == 404
    assert c.patch('/products/1/stock', json={'expected_version':0,'delta':-1}).status_code == 422

def test_persistence(tmp_path):
    path = tmp_path/'stock.db'
    c = TestClient(create_app(path))
    c.patch('/products/1/stock', json={'expected_version':1,'delta':5})
    other_app = TestClient(create_app(path))
    assert other_app.get('/products/1').json()['stock'] == 15
