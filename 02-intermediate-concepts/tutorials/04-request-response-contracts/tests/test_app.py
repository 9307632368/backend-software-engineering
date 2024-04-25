from fastapi.testclient import TestClient
from app import app

client=TestClient(app)
data={'customer_name':'  Ada   Lovelace  ','address':{'city':'Pune','postal_code':'411001'},'boxes':2}

def test_output_contract():
    r=client.post('/v1/shipments',json={**data,'internal_note':'do not expose'})
    assert r.status_code==201
    assert r.json()['customer_name']=='Ada Lovelace'
    assert 'internal_note' not in r.json()

def test_enum():
    r=client.post('/v1/shipments',json={**data,'priority':'urgent'})
    assert r.json()['estimated_days']==1

def test_nested_validation():
    r=client.post('/v1/shipments',json={**data,'address':{'city':'Pune','postal_code':'bad'}})
    assert r.status_code==422

def test_unknown_fields_blocked():
    assert client.post('/v1/shipments',json={**data,'is_admin':True}).status_code==422
