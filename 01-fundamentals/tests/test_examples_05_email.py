from fastapi.testclient import TestClient

def test_background_email_and_template(load_example):
    module = load_example("05-email-notification-service")
    sender = module.DemoSender()
    with TestClient(module.create_app(sender)) as api:
        result = api.post("/notifications", json={"to_email": "learner@example.com", "name": "Asha", "template": "welcome"})
        assert result.status_code == 202
        assert result.json()["status"] == "queued"
        assert len(sender.sent) == 1
        assert "Hi Asha" in sender.sent[0].body
        result = api.post("/notifications", json={"to_email": "learner@example.com", "name": "Asha", "template": "order", "order_id": "A104"})
        assert result.status_code == 202
        assert "A104" in api.get("/demo-outbox").json()[-1]["body"]

def test_email_validation(load_example):
    module = load_example("05-email-notification-service")
    with TestClient(module.create_app()) as api:
        base = {"to_email": "test@example.com", "name": "Asha"}
        assert api.post("/notifications", json={**base, "template": "unknown"}).status_code == 422
        assert api.post("/notifications", json={**base, "template": "order"}).status_code == 422
        assert api.post("/notifications", json={**base, "to_email": "not-email", "template": "welcome"}).status_code == 422
