from fastapi.testclient import TestClient
from app import create_app

def test_create_redirect_and_hits(tmp_path):
    c = TestClient(create_app(tmp_path/'short.db', token_generator=lambda:'abc123'))
    r = c.post('/links', json={'url':'https://example.com/hello', 'ttl_seconds':60})
    assert r.status_code == 201
    redirect = c.get('/r/abc123', follow_redirects=False)
    assert redirect.status_code == 307
    assert redirect.headers['location'] == 'https://example.com/hello'
    assert c.get('/links/abc123/stats').json()['hits'] == 1

def test_expiration_and_missing(tmp_path):
    clock=[100]
    c = TestClient(create_app(tmp_path/'short.db', clock=lambda:clock[0], token_generator=lambda:'token'))
    c.post('/links',json={'url':'https://example.org', 'ttl_seconds':2})
    clock[0]=103
    assert c.get('/r/token').status_code == 410
    assert c.get('/r/missing').status_code == 404

def test_invalid_url_and_collision(tmp_path):
    c = TestClient(create_app(tmp_path/'short.db',token_generator=lambda:'same'))
    assert c.post('/links',json={'url':'javascript:alert(1)'}).status_code == 422
    assert c.post('/links',json={'url':'https://example.com'}).status_code == 201
    assert c.post('/links',json={'url':'https://example.com'}).status_code == 503
