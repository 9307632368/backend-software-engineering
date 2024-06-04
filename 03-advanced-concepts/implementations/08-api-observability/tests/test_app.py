from fastapi.testclient import TestClient
from app import create_app

def test_request_ids_and_operational_endpoints():
    c=TestClient(create_app())
    r=c.get('/health/live')
    assert r.status_code == 200
    assert len(r.headers['X-Request-ID'])==32
    assert c.get('/health/ready').json()['status']=='ready'
    assert c.get('/work/2').json()['result']=='processed'
    assert c.get('/work/0').status_code==404

def test_metrics_use_route_pattern_not_actual_id():
    c=TestClient(create_app())
    c.get('/work/222')
    c.get('/work/333')
    data=c.get('/metrics').json()
    rows=[r for r in data['requests'] if r['route']=='/work/{item_id}']
    assert len(rows)==1 and rows[0]['count']==2
    assert all('222' not in r['route'] for r in data['requests'])

def test_unique_generated_ids_even_with_bad_incoming_header():
    c=TestClient(create_app())
    a=c.get('/work/1',headers={'X-Request-ID':'malicious\nheader'})
    b=c.get('/work/1')
    assert a.headers['X-Request-ID']!=b.headers['X-Request-ID']
