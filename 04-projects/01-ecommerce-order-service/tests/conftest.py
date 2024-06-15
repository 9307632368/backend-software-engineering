import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import create_app
from app.core import hash_password
from app.models import User

@pytest.fixture
def ctx(tmp_path):
    app = create_app(database_url=f"sqlite:///{tmp_path / 'test.db'}", jwt_secret="a-test-secret-that-is-long-enough")
    with TestClient(app) as client:
        yield client, app

@pytest.fixture
def account(ctx):
    client, app = ctx
    def make(email, role="customer"):
        with app.state.session_factory() as session:
            user = User(email=email, password_hash=hash_password("password123"), role=role)
            session.add(user)
            session.commit()
        token = client.post("/auth/login", json={"email": email, "password": "password123"}).json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return make
