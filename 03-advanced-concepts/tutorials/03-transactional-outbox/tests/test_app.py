from fastapi.testclient import TestClient
from app import create_app, InMemoryPublisher

def test_order_and_event_are_committed(tmp_path):
    c = TestClient(create_app(tmp_path/'events.db'))
    body = c.post('/orders', json={'sku':'PEN','quantity':2})
    assert body.status_code == 201
    events = c.get('/events').json()
    assert len(events) == 1
    assert events[0]['order_id'] == body.json()['id']
    assert events[0]['status'] == 'pending'

def test_dispatch_failure_then_retry(tmp_path):
    publisher = InMemoryPublisher()
    publisher.fail_next = True
    c = TestClient(create_app(tmp_path/'events.db', publisher))
    c.post('/orders',json={'sku':'PEN','quantity':2})
    assert c.post('/worker/dispatch').json() == {'sent':0, 'failed':1}
    assert c.get('/events').json()[0]['attempts'] == 1
    assert c.post('/worker/dispatch').json() == {'sent':1, 'failed':0}
    assert c.get('/events').json()[0]['status'] == 'sent'
    assert len(publisher.published) == 1

def test_invalid_order_creates_nothing(tmp_path):
    c = TestClient(create_app(tmp_path/'events.db'))
    assert c.post('/orders',json={'sku':'PEN','quantity':0}).status_code == 422
    assert c.get('/events').json() == []
