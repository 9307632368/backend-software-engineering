def ticket(client, user):
    response = client.post("/tickets", headers=user,
        json={"subject": "Unable to check order", "description": "After login the order page does not open", "priority": "high"})
    assert response.status_code == 201, response.text
    return response.json()["id"]

def test_customer_ticket_isolation_and_private_notes(ctx, account):
    client, _ = ctx
    a = account("person-a@example.com")
    b = account("person-b@example.com")
    agent = account("agent@example.com", "agent")
    tid = ticket(client, a)
    assert client.get(f"/tickets/{tid}", headers=b).status_code == 404
    assert client.get("/tickets", headers=b).json() == []
    assert client.post(f"/tickets/{tid}/comments", headers=a, json={"body": "Please help", "internal": True}).status_code == 403
    assert client.post(f"/tickets/{tid}/comments", headers=agent, json={"body": "Customer missing invoice", "internal": True}).status_code == 201
    assert client.post(f"/tickets/{tid}/comments", headers=agent, json={"body": "Checking now", "internal": False}).status_code == 201
    assert [c["body"] for c in client.get(f"/tickets/{tid}", headers=a).json()["comments"]] == ["Checking now"]
    assert len(client.get(f"/tickets/{tid}", headers=agent).json()["comments"]) == 2

def test_assignment_status_and_audit(ctx, account):
    client, _ = ctx
    owner = account("owner@example.com")
    agent = account("staff@example.com", "agent")
    tid = ticket(client, owner)
    who = client.get("/auth/me", headers=agent).json()["id"]
    assert client.patch(f"/tickets/{tid}/assign", headers=owner, json={"agent_id": who}).status_code == 403
    assert client.patch(f"/tickets/{tid}/assign", headers=agent, json={"agent_id": who}).status_code == 200
    assert client.patch(f"/tickets/{tid}/status", headers=agent, json={"status": "resolved"}).status_code == 409
    assert client.patch(f"/tickets/{tid}/status", headers=agent, json={"status": "in_progress"}).status_code == 200
    assert client.patch(f"/tickets/{tid}/status", headers=agent, json={"status": "resolved"}).status_code == 200
    assert client.patch(f"/tickets/{tid}/status", headers=agent, json={"status": "reopened"}).status_code == 200
    assert client.patch(f"/tickets/{tid}/status", headers=agent, json={"status": "closed"}).status_code == 200
    assert client.post(f"/tickets/{tid}/comments", headers=owner, json={"body": "Thanks"}).status_code == 409
    assert client.get(f"/tickets/{tid}/events", headers=owner).status_code == 403
    assert len(client.get(f"/tickets/{tid}/events", headers=agent).json()) == 6

def test_input_validation_and_auth(ctx, account):
    client, _ = ctx
    a = account("account@example.com")
    assert client.post("/tickets", json={"subject":"test", "description":"this is enough"}).status_code == 401
    assert client.post("/tickets", headers=a, json={"subject":"ab", "description":"short"}).status_code == 422
    assert client.get("/health").json() == {"status":"ok"}


def test_admin_agent_provisioning(ctx, account):
    client, _ = ctx
    admin = account("admin3@example.com", "admin")
    customer = account("customer3@example.com")
    data = {"email": "newagent@example.com", "password": "passphrase123"}
    assert client.post("/staff/agents", headers=customer, json=data).status_code == 403
    response = client.post("/staff/agents", headers=admin, json=data)
    assert response.status_code == 201
    assert response.json()["role"] == "agent"
    assert client.post("/staff/agents", headers=admin, json=data).status_code == 409
    token = client.post("/auth/login", json=data).json()["access_token"]
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {token}"}).json()["role"] == "agent"


def test_public_comment_and_customer_cannot_advance_state(ctx, account):
    client, _ = ctx
    customer = account("public-customer@example.com")
    agent = account("public-agent@example.com", "agent")
    tid = ticket(client, customer)
    public = client.post(f"/tickets/{tid}/comments", headers=customer, json={"body":"I can attach more information"})
    assert public.status_code == 201
    assert client.get(f"/tickets/{tid}", headers=customer).json()["comments"][0]["body"] == "I can attach more information"
    assert client.patch(f"/tickets/{tid}/status", headers=customer, json={"status":"in_progress"}).status_code == 403
    assert client.patch(f"/tickets/{tid}/assign", headers=agent, json={"agent_id": 99999}).status_code == 422
    assert len(client.get("/tickets", headers=agent).json()) == 1
    assert len(client.get("/tickets", headers=customer).json()) == 1


def test_ticket_data_survives_new_app_instance(ctx, account):
    client, app = ctx
    owner = account("save-customer@example.com")
    tid = ticket(client, owner)
    from app.main import create_app
    from fastapi.testclient import TestClient
    with TestClient(create_app(str(app.state.engine.url), jwt_secret="a-test-secret-that-is-long-enough")) as fresh:
        assert fresh.get(f"/tickets/{tid}", headers=owner).json()["subject"] == "Unable to check order"
