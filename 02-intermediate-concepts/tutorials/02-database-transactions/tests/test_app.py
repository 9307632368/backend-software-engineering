from fastapi.testclient import TestClient
from app import create_app

def test_transfer_is_atomic_for_business_rejection(tmp_path):
    with TestClient(create_app('sqlite:///'+str(tmp_path/'test.db'))) as c:
        a=c.post('/wallets',json={'owner':'Alice','initial_paise':1000}).json()['id']
        b=c.post('/wallets',json={'owner':'Bob','initial_paise':0}).json()['id']
        assert c.post('/transfers',json={'from_id':a,'to_id':b,'amount_paise':1200}).status_code == 409
        assert c.get(f'/wallets/{a}').json()['balance_paise'] == 1000
        assert c.get(f'/wallets/{b}').json()['balance_paise'] == 0
        assert c.post('/transfers',json={'from_id':a,'to_id':b,'amount_paise':350}).status_code == 200
        assert c.get(f'/wallets/{a}').json()['balance_paise'] == 650
        assert c.get(f'/wallets/{b}').json()['balance_paise'] == 350

def test_wallet_conflict(tmp_path):
    with TestClient(create_app('sqlite:///'+str(tmp_path/'dupe.db'))) as c:
        data={'owner':'Alice','initial_paise':10}
        assert c.post('/wallets',json=data).status_code == 201
        assert c.post('/wallets',json=data).status_code == 409
        assert c.post('/wallets',json={'owner':'E','initial_paise':2}).status_code == 422

def test_invalid_transfer(tmp_path):
    with TestClient(create_app('sqlite:///'+str(tmp_path/'invalid.db'))) as c:
        assert c.post('/transfers',json={'from_id':1,'to_id':1,'amount_paise':10}).status_code == 400
        assert c.post('/transfers',json={'from_id':1,'to_id':2,'amount_paise':10}).status_code == 404
