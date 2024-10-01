import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from hands_on.idempotent_payments import create_app as payments_app
from hands_on.sliding_window_rate_limit import SlidingWindowLimiter, create_app as limit_app
from hands_on.concurrent_stock_orders import create_app as orders_app
from hands_on.audit_log_pagination import create_app as audit_app
from hands_on.signed_webhook import create_app as webhook_app, signature
from hands_on.retry_job_queue import create_app as jobs_app


def test_payment_created_and_counted(tmp_path):
    c = TestClient(payments_app(str(tmp_path / 'pay.sqlite')))
    r = c.post('/payments', headers={'Idempotency-Key': 'once'},
               json={'customer_id': 'c1', 'amount_paise': 1599})
    assert r.status_code == 201
    assert r.json()['replayed'] is False
    assert c.get('/payments/count').json()['count'] == 1


def test_payment_retry_is_not_double_charged(tmp_path):
    c = TestClient(payments_app(str(tmp_path / 'pay.sqlite')))
    kwargs = dict(headers={'Idempotency-Key': 'unique-1'}, json={'customer_id': 'c1', 'amount_paise': 1599})
    first, second = c.post('/payments', **kwargs), c.post('/payments', **kwargs)
    assert second.status_code == 201
    assert second.json()['payment_id'] == first.json()['payment_id']
    assert second.json()['replayed'] is True
    assert c.get('/payments/count').json()['count'] == 1


def test_payment_key_conflict(tmp_path):
    c = TestClient(payments_app(str(tmp_path / 'p.sqlite')))
    h = {'Idempotency-Key': 'same'}
    assert c.post('/payments', headers=h, json={'customer_id': 'c', 'amount_paise': 100}).status_code == 201
    assert c.post('/payments', headers=h, json={'customer_id': 'c', 'amount_paise': 200}).status_code == 409
    assert c.get('/payments/count').json()['count'] == 1


def test_payment_key_scoped_to_customer(tmp_path):
    c = TestClient(payments_app(str(tmp_path / 'p.sqlite')))
    for customer in ['c1', 'c2']:
        assert c.post('/payments', headers={'Idempotency-Key': 'key'},
                      json={'customer_id': customer, 'amount_paise': 100}).status_code == 201
    assert c.get('/payments/count').json()['count'] == 2


@pytest.mark.parametrize('bad', [0, -9, 50000001])
def test_payment_invalid_amount(tmp_path, bad):
    c = TestClient(payments_app(str(tmp_path / 'p.sqlite')))
    assert c.post('/payments', headers={'Idempotency-Key': 'key'},
                  json={'customer_id': 'a', 'amount_paise': bad}).status_code == 422


def test_payment_missing_key(tmp_path):
    c = TestClient(payments_app(str(tmp_path / 'p.sqlite')))
    assert c.post('/payments', json={'customer_id': 'a', 'amount_paise': 100}).status_code == 422


def test_payment_data_survives_app_recreation(tmp_path):
    path = str(tmp_path / 'p.sqlite')
    TestClient(payments_app(path)).post('/payments', headers={'Idempotency-Key': 'a'},
                                       json={'customer_id': 'a', 'amount_paise': 123})
    assert TestClient(payments_app(path)).get('/payments/count').json()['count'] == 1


def test_limiter_first_requests_pass_then_429():
    now = [100.0]
    limiter = SlidingWindowLimiter(2, 60, clock=lambda: now[0])
    c = TestClient(limit_app(limiter))
    h = {'X-API-Key': 'a'}
    assert c.get('/search?q=cats', headers=h).status_code == 200
    assert c.get('/search?q=dogs', headers=h).status_code == 200
    blocked = c.get('/search?q=fish', headers=h)
    assert blocked.status_code == 429
    assert blocked.headers['retry-after'] == '60'


def test_limiter_keys_are_separate():
    lim = SlidingWindowLimiter(1, 30, clock=lambda: 0.0)
    c = TestClient(limit_app(lim))
    for key in ['a', 'b']:
        assert c.get('/search?q=x', headers={'X-API-Key': key}).status_code == 200
    assert c.get('/search?q=x', headers={'X-API-Key': 'a'}).status_code == 429


def test_limiter_window_expires():
    now = [1.0]
    lim = SlidingWindowLimiter(1, 10, clock=lambda: now[0])
    c = TestClient(limit_app(lim))
    h = {'X-API-Key': 'a'}
    assert c.get('/search?q=x', headers=h).status_code == 200
    now[0] = 10.9
    assert c.get('/search?q=x', headers=h).status_code == 429
    now[0] = 11.0
    assert c.get('/search?q=x', headers=h).status_code == 200


def test_limiter_missing_key():
    assert TestClient(limit_app()).get('/search?q=x').status_code == 422


def test_limiter_rejects_bad_config():
    with pytest.raises(ValueError):
        SlidingWindowLimiter(0, 1)


def test_stock_place_order_decrements(tmp_path):
    c = TestClient(orders_app(str(tmp_path / 'stock.sqlite')))
    assert c.post('/stock', json={'sku': 'ITEM-01', 'quantity': 5}).status_code == 201
    assert c.post('/orders', json={'sku': 'ITEM-01', 'quantity': 3}).status_code == 201
    assert c.get('/stock/ITEM-01').json()['available'] == 2


def test_stock_cannot_oversell(tmp_path):
    c = TestClient(orders_app(str(tmp_path / 's.sqlite')))
    c.post('/stock', json={'sku': 'ITEM-01', 'quantity': 2})
    assert c.post('/orders', json={'sku': 'ITEM-01', 'quantity': 3}).status_code == 409
    assert c.get('/stock/ITEM-01').json()['available'] == 2


def test_stock_unknown_sku_and_duplicate(tmp_path):
    c = TestClient(orders_app(str(tmp_path / 's.sqlite')))
    assert c.get('/stock/unknown').status_code == 404
    assert c.post('/orders', json={'sku': 'unknown', 'quantity': 1}).status_code == 404
    c.post('/stock', json={'sku': 'ITEM-01', 'quantity': 3})
    assert c.post('/stock', json={'sku': 'ITEM-01', 'quantity': 3}).status_code == 409


def test_stock_invalid_values(tmp_path):
    c = TestClient(orders_app(str(tmp_path / 's.sqlite')))
    assert c.post('/orders', json={'sku': 'ITEM-01', 'quantity': 0}).status_code == 422
    assert c.post('/stock', json={'sku': 'ITEM-01', 'quantity': -1}).status_code == 422


def test_concurrent_buyers_do_not_oversell(tmp_path):
    path = str(tmp_path / 's.sqlite')
    c = TestClient(orders_app(path))
    c.post('/stock', json={'sku': 'WIDGET', 'quantity': 1})
    def buy(_):
        return c.post('/orders', json={'sku': 'WIDGET', 'quantity': 1}).status_code
    with ThreadPoolExecutor(max_workers=4) as pool:
        statuses = list(pool.map(buy, range(4)))
    assert statuses.count(201) == 1
    assert statuses.count(409) == 3
    assert c.get('/stock/WIDGET').json()['available'] == 0


def test_audit_empty_page(tmp_path):
    c = TestClient(audit_app(str(tmp_path / 'events.sqlite')))
    assert c.get('/events').json() == {'page': 1, 'size': 10, 'total': 0, 'pages': 0, 'items': []}


def test_audit_sorted_latest_first(tmp_path):
    c = TestClient(audit_app(str(tmp_path / 'events.sqlite')))
    for event in ['login', 'upload', 'logout']:
        c.post('/events', json={'actor': 'u1', 'event_type': event})
    res = c.get('/events?size=2').json()
    assert [e['event_type'] for e in res['items']] == ['logout', 'upload']
    assert (res['total'], res['pages']) == (3, 2)
    assert [e['event_type'] for e in c.get('/events?page=2&size=2').json()['items']] == ['login']


def test_audit_filter(tmp_path):
    c = TestClient(audit_app(str(tmp_path / 'e.sqlite')))
    for event in ['login', 'upload', 'login']:
        c.post('/events', json={'actor': 'a', 'event_type': event})
    result = c.get('/events?event_type=login').json()
    assert result['total'] == 2
    assert all(item['event_type'] == 'login' for item in result['items'])


def test_audit_invalid_page_size(tmp_path):
    c = TestClient(audit_app(str(tmp_path / 'e.sqlite')))
    assert c.get('/events?page=0').status_code == 422
    assert c.get('/events?size=100').status_code == 422


def signed_request(c, ts, raw, secret='test-secret', sig=None):
    h = {'X-Webhook-Timestamp': str(ts),
         'X-Webhook-Signature': sig if sig is not None else signature(secret, ts, raw),
         'Content-Type': 'application/json'}
    return c.post('/webhook', content=raw, headers=h)


def test_webhook_good_signature():
    c = TestClient(webhook_app('test-secret', clock=lambda: 1000))
    r = signed_request(c, 1000, b'{"event_id":"ev1"}')
    assert r.status_code == 200
    assert r.json()['status'] == 'accepted'


def test_webhook_duplicate_event():
    c = TestClient(webhook_app('test-secret', clock=lambda: 1000))
    raw = b'{"event_id":"ev1"}'
    signed_request(c, 1000, raw)
    assert signed_request(c, 1000, raw).json()['status'] == 'duplicate'


def test_webhook_bad_signature():
    c = TestClient(webhook_app('test-secret', clock=lambda: 1000))
    assert signed_request(c, 1000, b'{"event_id":"ev1"}', sig='0' * 64).status_code == 401


def test_webhook_stale_timestamp():
    c = TestClient(webhook_app('test-secret', clock=lambda: 1000))
    assert signed_request(c, 699, b'{"event_id":"ev1"}').status_code == 401


def test_webhook_malformed_json():
    c = TestClient(webhook_app('test-secret', clock=lambda: 1000))
    assert signed_request(c, 1000, b'not json').status_code == 400


def test_webhook_missing_event_id():
    c = TestClient(webhook_app('test-secret', clock=lambda: 1000))
    assert signed_request(c, 1000, b'{}').status_code == 422


def test_webhook_invalid_timestamp():
    c = TestClient(webhook_app('test-secret', clock=lambda: 1000))
    assert c.post('/webhook', content=b'{}', headers={
        'X-Webhook-Timestamp': 'bad', 'X-Webhook-Signature': 'x'}).status_code == 400


def test_jobs_success_and_persistence(tmp_path):
    path = str(tmp_path / 'jobs.sqlite')
    called = []
    c = TestClient(jobs_app(path, handler=lambda task, data: called.append((task, data))))
    job = c.post('/jobs', json={'task': 'send_email', 'payload': {'to': 'a@example.test'}}).json()
    assert job['state'] == 'pending'
    assert c.post('/worker/run-once').json()['state'] == 'completed'
    assert called == [('send_email', {'to': 'a@example.test'})]
    assert TestClient(jobs_app(path)).get(f'/jobs/{job["job_id"]}').json()['attempts'] == 1


def test_jobs_no_jobs_to_run(tmp_path):
    c = TestClient(jobs_app(str(tmp_path / 'jobs.sqlite')))
    assert c.post('/worker/run-once').json() == {'processed': False}


def test_jobs_retry_then_success(tmp_path):
    counter = [0]
    def flaky(task, data):
        counter[0] += 1
        if counter[0] == 1:
            raise RuntimeError('temporarily unavailable')
    c = TestClient(jobs_app(str(tmp_path / 'jobs.sqlite'), handler=flaky))
    job_id = c.post('/jobs', json={'task': 'sync'}).json()['job_id']
    assert c.post('/worker/run-once').json()['state'] == 'pending'
    assert c.post('/worker/run-once').json()['state'] == 'completed'
    assert c.get(f'/jobs/{job_id}').json()['attempts'] == 2


def test_jobs_dead_letter_after_3_failures(tmp_path):
    def fail(task, data):
        raise RuntimeError('unavailable')
    c = TestClient(jobs_app(str(tmp_path / 'jobs.sqlite'), handler=fail))
    job_id = c.post('/jobs', json={'task': 'sync'}).json()['job_id']
    for _ in range(2):
        assert c.post('/worker/run-once').json()['state'] == 'pending'
    assert c.post('/worker/run-once').json()['state'] == 'dead_letter'
    assert c.get(f'/jobs/{job_id}').json()['attempts'] == 3
    assert c.get(f'/jobs/{job_id}').json()['error'] == 'unavailable'
    assert c.post('/worker/run-once').json()['processed'] is False


def test_jobs_missing_id(tmp_path):
    c = TestClient(jobs_app(str(tmp_path / 'jobs.sqlite')))
    assert c.get('/jobs/99').status_code == 404


def test_jobs_invalid_task(tmp_path):
    c = TestClient(jobs_app(str(tmp_path / 'jobs.sqlite')))
    assert c.post('/jobs', json={'task': ''}).status_code == 422


def test_jobs_attempt_config(tmp_path):
    with pytest.raises(ValueError):
        jobs_app(str(tmp_path / 'jobs.sqlite'), max_attempts=0)
