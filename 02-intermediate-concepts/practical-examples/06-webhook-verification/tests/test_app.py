import hashlib,hmac,json
from fastapi.testclient import TestClient
from app import create_app

def signed(data, secret='test-secret',id='evt-1'):
    raw=json.dumps(data,separators=(',',':')).encode()
    signature='sha256='+hmac.new(secret.encode(),raw,hashlib.sha256).hexdigest()
    return raw, {'x-event-id':id,'x-signature':signature,'content-type':'application/json'}

def test_event_duplicate(tmp_path):
    raw,h=signed({'type':'order.created','resource_id':'o1'})
    with TestClient(create_app(str(tmp_path/'events.db'), secret='test-secret')) as c:
        r=c.post('/webhooks/events',content=raw,headers=h)
        assert r.status_code==200 and r.json()['result']=='recorded'
        r=c.post('/webhooks/events',content=raw,headers=h)
        assert r.json()['result']=='duplicate'

def test_bad_signature(tmp_path):
    raw,h=signed({'type':'order.created','resource_id':'o1'})
    h['x-signature']='sha256=000000'
    with TestClient(create_app(str(tmp_path/'bad.db'), secret='test-secret')) as c:
        assert c.post('/webhooks/events',content=raw,headers=h).status_code==401

def test_invalid_event(tmp_path):
    raw,h=signed({'wrong':'payload'})
    with TestClient(create_app(str(tmp_path/'missing.db'), secret='test-secret')) as c:
        assert c.post('/webhooks/events',content=raw,headers=h).status_code==422

def test_missing_secret(tmp_path):
    raw,h=signed({'type':'x','resource_id':'y'})
    with TestClient(create_app(str(tmp_path/'no-secret.db'),secret='')) as c:
        assert c.post('/webhooks/events',content=raw,headers=h).status_code==503
