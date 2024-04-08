from fastapi.testclient import TestClient

def test_registration_and_login(load_example):
    module = load_example("01-user-registration-login")
    with TestClient(module.create_app()) as api:
        user = {"email": "Student@Example.com", "password": "myPassword123"}
        response = api.post("/users/register", json=user)
        assert response.status_code == 201
        assert response.json()["email"] == "student@example.com"
        assert "password" not in response.text
        assert api.post("/users/login", json=user).status_code == 200
        assert api.post("/users/register", json=user).status_code == 409
        assert api.post("/users/login", json={**user, "password": "wrongPassword"}).status_code == 401
        assert api.post("/users/login", json={"email": "missing@example.com", "password": "password123"}).status_code == 401

def test_password_is_salted(load_example):
    module = load_example("01-user-registration-login")
    one = module.hash_password("myPassword123")
    two = module.hash_password("myPassword123")
    assert one != two
    assert module.password_matches("myPassword123", one)
    assert not module.password_matches("wrongPassword", two)

def test_registration_validation(load_example):
    module = load_example("01-user-registration-login")
    with TestClient(module.create_app()) as api:
        assert api.post("/users/register", json={"email": "bad", "password": "abcdefgh"}).status_code == 422
        assert api.post("/users/register", json={"email": "a@b.co", "password": "short"}).status_code == 422
