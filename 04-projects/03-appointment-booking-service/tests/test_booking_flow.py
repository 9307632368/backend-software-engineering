from datetime import datetime, timedelta, timezone

def next_slot():
    moment = datetime.now(timezone.utc) + timedelta(days=2)
    moment = moment.replace(hour=10, minute=0, second=0, microsecond=0)
    return moment.isoformat().replace("+00:00", "Z")

def service_and_slot(client, admin):
    r = client.post("/services", headers=admin, json={"name": "Tech Consultation", "description": "30 minute session"})
    assert r.status_code == 201, r.text
    service_id = r.json()["id"]
    r = client.post(f"/services/{service_id}/slots", headers=admin, json={"starts_at": next_slot()})
    assert r.status_code == 201, r.text
    return service_id, r.json()["id"]

def test_booking_retry_cancel_and_reuse_slot(ctx, account):
    client, _ = ctx
    admin = account("admin@example.com", "admin")
    first = account("one@example.com")
    second = account("two@example.com")
    sid, slot_id = service_and_slot(client, admin)
    assert len(client.get(f"/services/{sid}/slots").json()) == 1
    data = {"slot_id": slot_id}
    h = {**first, "Idempotency-Key": "booking-key-111"}
    original = client.post("/bookings", headers=h, json=data)
    assert original.status_code == 201, original.text
    assert client.post("/bookings", headers=h, json=data).json()["id"] == original.json()["id"]
    assert client.post("/bookings", headers={**second,"Idempotency-Key": "booking-key-222"}, json=data).status_code == 409
    assert client.get(f"/services/{sid}/slots").json() == []
    bid = original.json()["id"]
    assert client.get(f"/bookings/{bid}", headers=second).status_code == 404
    assert client.post(f"/bookings/{bid}/cancel", headers=first).status_code == 200
    assert client.post(f"/bookings/{bid}/cancel", headers=first).status_code == 409
    assert len(client.get(f"/services/{sid}/slots").json()) == 1
    assert client.post("/bookings", headers={**second,"Idempotency-Key": "booking-key-222"}, json=data).status_code == 201
    assert [x["action"] for x in client.get(f"/bookings/{bid}/events", headers=first).json()] == ["confirmed", "cancelled"]

def test_slot_date_checks_and_permissions(ctx, account):
    client, _ = ctx
    admin = account("staff@example.com", "admin")
    customer = account("person@example.com")
    assert client.post("/services", headers=customer, json={"name":"New Service"}).status_code == 403
    sid, slot_id = service_and_slot(client, admin)
    assert client.post(f"/services/{sid}/slots", headers=admin, json={"starts_at": next_slot()}).status_code == 409
    assert client.post(f"/services/{sid}/slots", headers=admin, json={"starts_at": "2024-06-12T10:00:00Z"}).status_code == 422
    assert client.post(f"/services/{sid}/slots", headers=admin, json={"starts_at": "2030-06-12T10:00:00"}).status_code == 422
    assert client.post("/bookings", headers=customer, json={"slot_id": slot_id}).status_code == 422
    assert client.get("/bookings", headers=customer).json() == []
    assert client.get("/bookings").status_code == 401


def test_booking_persisted_and_owner_scope(ctx, account):
    client, app = ctx
    admin = account("save-admin@example.com", "admin")
    owner = account("save-owner@example.com")
    stranger = account("save-stranger@example.com")
    _, sid = service_and_slot(client, admin)
    booking = client.post("/bookings", headers={**owner, "Idempotency-Key": "save-booking-0001"}, json={"slot_id": sid})
    assert booking.status_code == 201
    bid = booking.json()["id"]
    assert client.post(f"/bookings/{bid}/cancel", headers=stranger).status_code == 404
    assert client.get(f"/bookings/{bid}/events", headers=stranger).status_code == 404
    from app.main import create_app
    from fastapi.testclient import TestClient
    with TestClient(create_app(str(app.state.engine.url), jwt_secret="a-test-secret-that-is-long-enough")) as fresh:
        assert fresh.get(f"/bookings/{bid}", headers=owner).json()["status"] == "confirmed"


def test_rbac_duplicates_and_iso_date(ctx, account):
    client, _ = ctx
    admin = account("next-admin@example.com", "admin")
    customer = account("next-customer@example.com")
    assert client.post("/services", headers=customer, json={"name":"No permission"}).status_code == 403
    srv = client.post("/services", headers=admin, json={"name":"Onboarding", "description":"demo"})
    assert srv.status_code == 201
    service_id = srv.json()["id"]
    assert client.post("/services", headers=admin, json={"name":"Onboarding"}).status_code == 409
    bad = client.post(f"/services/{service_id}/slots", headers=admin, json={"starts_at":"2035-01-01T09:15:00Z"})
    assert bad.status_code == 422
    assert client.post("/bookings", headers={**customer,"Idempotency-Key":"invalid-slot-001"},json={"slot_id":9999}).status_code == 404
