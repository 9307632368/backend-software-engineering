import json
import pytest
from fastapi.testclient import TestClient
from payment_hooks.app import create_app,sign

SECRET="test-secret"
KEY="internal-test-key"
NOW=1734600000  # Dec 2024 timestamp, stable local test clock

@pytest.fixture
def client(tmp_path):
    api=create_app(tmp_path/"payments.sqlite3",secret=SECRET,internal_key=KEY,clock=lambda:NOW)
    return TestClient(api)


def register(client,payment="pay_01",amount=1199):
    return client.post("/internal/payments",json={"payment_id":payment,"amount_cents":amount},
                       headers={"X-Internal-Api-Key":KEY})


def lookup(client,payment="pay_01"):
    return client.get(f"/internal/payments/{payment}",headers={"X-Internal-Api-Key":KEY})


def hook(client,event_id="evt_01",payment="pay_01",event_type="payment.succeeded",amount=1199,
         timestamp=NOW,signature=None):
    data={"event_id":event_id,"payment_id":payment,"type":event_type,"amount_cents":amount}
    raw=json.dumps(data,separators=(",",":")).encode()
    sig=signature if signature is not None else sign(SECRET,timestamp,raw)
    return client.post("/webhooks/payment",content=raw,
      headers={"Content-Type":"application/json","X-Webhook-Timestamp":str(timestamp),"X-Webhook-Signature":sig})


def test_register_and_signed_success(client):
    assert register(client).status_code==201
    assert hook(client).json()=={"outcome":"applied","duplicate":False}
    assert lookup(client).json()["state"]=="succeeded"


def test_duplicate_event_not_double_applied(client):
    register(client)
    assert hook(client).status_code==200
    again=hook(client)
    assert again.json()=={"outcome":"applied","duplicate":True}
    assert lookup(client).json()["state"]=="succeeded"


def test_invalid_signature_rejected(client):
    register(client)
    assert hook(client,signature="bad").status_code==401
    assert lookup(client).json()["state"]=="pending"


def test_stale_webhook_rejected(client):
    register(client)
    assert hook(client,timestamp=NOW-601).status_code==401


def test_unmatched_then_reconciled(client):
    assert hook(client,payment="pay_early").status_code==202
    assert register(client,payment="pay_early").status_code==201
    run=client.post("/internal/reconcile",headers={"X-Internal-Api-Key":KEY})
    assert run.json()=={"applied":1,"ignored":0,"awaiting_payment":0}
    assert lookup(client,"pay_early").json()["state"]=="succeeded"
    assert client.post("/internal/reconcile",headers={"X-Internal-Api-Key":KEY}).json()["applied"]==0


def test_event_id_cannot_change_payload(client):
    register(client)
    hook(client)
    assert hook(client,event_type="payment.failed").status_code==409
    assert lookup(client).json()["state"]=="succeeded"


def test_terminal_success_not_overwritten(client):
    register(client)
    assert hook(client).json()["outcome"]=="applied"
    assert hook(client,event_id="evt_late",event_type="payment.failed").json()["outcome"]=="ignored"
    assert lookup(client).json()["state"]=="succeeded"


def test_webhook_amount_must_match(client):
    register(client)
    assert hook(client,amount=1000).status_code==409
    assert lookup(client).json()["state"]=="pending"


def test_bad_internal_key_and_duplicate_payment(client):
    assert register(client).status_code==201
    assert register(client).status_code==409
    assert client.get("/internal/payments/pay_01").status_code==401
    assert client.post("/internal/reconcile").status_code==401


def test_failed_payment(client):
    register(client)
    assert hook(client,event_type="payment.failed").json()["outcome"]=="applied"
    assert lookup(client).json()["state"]=="failed"


def test_invalid_payload_after_valid_signature(client):
    raw=b'{"event_id":"evt","payment_id":"pay","type":"unknown","amount_cents":1}'
    assert client.post("/webhooks/payment",content=raw,headers={
        "X-Webhook-Timestamp":str(NOW),"X-Webhook-Signature":sign(SECRET,NOW,raw)
    }).status_code==422
