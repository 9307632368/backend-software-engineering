from fastapi.testclient import TestClient
from app import create_app

product={'sku':'MED-101','name':'Demo medical product','stock':5,'price_paise':1999}

def test_reserve_confirm_and_cancel(tmp_path):
    with TestClient(create_app(str(tmp_path/'a.db'))) as c:
        assert c.post('/products',json=product).status_code==201
        o1=c.post('/orders',json={'sku':'MED-101','quantity':3}).json()['id']
        assert c.get('/products/MED-101').json()['available']==2
        assert c.post('/orders',json={'sku':'MED-101','quantity':3}).status_code==409
        assert c.post(f'/orders/{o1}/confirm').json()['status']=='confirmed'
        item=c.get('/products/MED-101').json()
        assert item['stock']==2 and item['reserved']==0
        assert c.post(f'/orders/{o1}/confirm').status_code==409
        o2=c.post('/orders',json={'sku':'MED-101','quantity':2}).json()['id']
        assert c.post(f'/orders/{o2}/cancel').json()['status']=='cancelled'
        item=c.get('/products/MED-101').json()
        assert item['available']==2

def test_validation_missing_product(tmp_path):
    with TestClient(create_app(str(tmp_path/'b.db'))) as c:
        assert c.post('/orders',json={'sku':'missing','quantity':1}).status_code==404
        assert c.post('/products',json=product).status_code==201
        assert c.post('/products',json=product).status_code==409
        assert c.post('/orders',json={'sku':'MED-101','quantity':0}).status_code==422
        assert c.post('/orders/999/cancel').status_code==404

def test_data_survives_restart(tmp_path):
    location=str(tmp_path/'persist.db')
    with TestClient(create_app(location)) as c:
        c.post('/products',json=product)
        oid=c.post('/orders',json={'sku':'MED-101','quantity':2}).json()['id']
    with TestClient(create_app(location)) as c:
        assert c.get(f'/orders/{oid}').json()['status']=='reserved'
        assert c.get('/products/MED-101').json()['available']==3
