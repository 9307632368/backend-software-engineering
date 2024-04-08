from fastapi.testclient import TestClient
import jwt
from datetime import datetime, timezone, timedelta

SECRET = "local-testing-secret-with-at-least-32-chars"

def test_jwt_workflow(load_example):
    module = load_example("04-jwt-authentication")
    with TestClient(module.create_app(SECRET)) as api:
        user = {"username": "rohan2024", "password": "pass123456"}
        assert api.get("/me").status_code == 401
        assert api.post("/register", json=user).status_code == 201
        assert api.post("/register", json=user).status_code == 409
        assert api.post("/token", json={**user, "password": "notright123"}).status_code == 401
        token = api.post("/token", json=user).json()["access_token"]
        assert api.get("/me", headers={"Authorization": f"Bearer {token}"}).json()["username"] == "rohan2024"
        assert api.get("/me", headers={"Authorization": "Bearer invalid.token.value"}).status_code == 401

def test_expired_and_unsigned_tokens(load_example):
    module = load_example("04-jwt-authentication")
    with TestClient(module.create_app(SECRET)) as api:
        api.post("/register", json={"username": "student", "password": "pass123456"})
        expired = jwt.encode({"sub": "student", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)}, SECRET, algorithm="HS256")
        assert api.get("/me", headers={"Authorization": f"Bearer {expired}"}).status_code == 401
    with TestClient(module.create_app()) as api:
        api.post("/register", json={"username": "student", "password": "pass123456"})
        assert api.post("/token", json={"username": "student", "password": "pass123456"}).status_code == 503
