from fastapi.testclient import TestClient
from app import create_app

payload={'customer_id':'c-101','item_sku':'PEN-8','quantity':3,'unit_price_paise':1500}

def test_replay_and_conflicting_reuse(tmp_path):
    with TestClient(create_app(str(tmp_path/'a.db'))) as c:
        h={'idempotency-key':'cart-001'}
        first=c.post('/checkouts',json=payload,headers=h)
        assert first.status_code==201
        assert first.json()['replayed'] is False
        replay=c.post('/checkouts',json=payload,headers=h)
        assert replay.status_code==201
        assert replay.json()['replayed'] is True
        assert replay.json()['id']==first.json()['id']
        assert c.post('/checkouts',json={**payload,'quantity':2},headers=h).status_code==409

def test_missing_key_and_input_validation(tmp_path):
    with TestClient(create_app(str(tmp_path/'b.db'))) as c:
        assert c.post('/checkouts',json=payload).status_code==400
        assert c.post('/checkouts',json={**payload,'quantity':0},headers={'idempotency-key':'x'}).status_code==422

def test_persists_after_restart(tmp_path):
    db=str(tmp_path/'persist.db')
    with TestClient(create_app(db)) as c:
        item=c.post('/checkouts',json=payload,headers={'idempotency-key':'k1'}).json()
    with TestClient(create_app(db)) as c:
        assert c.get('/checkouts/'+str(item['id'])).json()['total_paise']==4500
