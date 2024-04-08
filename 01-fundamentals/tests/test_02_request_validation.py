from fastapi.testclient import TestClient

VALID = {
    "student_name": "  Ananya  ", "course_code": "cse401",
    "semester": 4, "mode": "online", "credits": 4,
}


def test_valid_enrollment_preview(load_tutorial):
    client = TestClient(load_tutorial("02-request-validation").app)
    res = client.post("/enrollments/preview", json=VALID)
    assert res.status_code == 201
    assert res.json()["student_name"] == "Ananya"
    assert res.json()["course_code"] == "CSE401"
    assert res.json()["enrollment_id"] == "PREVIEW-CSE401-4"


def test_invalid_semester(load_tutorial):
    client = TestClient(load_tutorial("02-request-validation").app)
    assert client.post("/enrollments/preview", json={**VALID, "semester": 9}).status_code == 422


def test_invalid_mode(load_tutorial):
    client = TestClient(load_tutorial("02-request-validation").app)
    assert client.post("/enrollments/preview", json={**VALID, "mode": "hybrid"}).status_code == 422


def test_unknown_field_rejected(load_tutorial):
    client = TestClient(load_tutorial("02-request-validation").app)
    assert client.post("/enrollments/preview", json={**VALID, "is_admin": True}).status_code == 422


def test_missing_field_rejected(load_tutorial):
    client = TestClient(load_tutorial("02-request-validation").app)
    value = {k: v for k, v in VALID.items() if k != "credits"}
    assert client.post("/enrollments/preview", json=value).status_code == 422
