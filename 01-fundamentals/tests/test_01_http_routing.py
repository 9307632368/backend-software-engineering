from fastapi.testclient import TestClient


def test_health(load_tutorial):
    client = TestClient(load_tutorial("01-http-and-routing").app)
    assert client.get("/health").json() == {"status": "ok"}


def test_list_all_books(load_tutorial):
    client = TestClient(load_tutorial("01-http-and-routing").app)
    response = client.get("/books")
    assert response.status_code == 200
    assert response.json()["count"] == 3


def test_book_filter(load_tutorial):
    client = TestClient(load_tutorial("01-http-and-routing").app)
    result = client.get("/books?category=systems").json()
    assert result["count"] == 2
    assert all(b["category"] == "systems" for b in result["items"])


def test_search_is_case_insensitive(load_tutorial):
    client = TestClient(load_tutorial("01-http-and-routing").app)
    assert client.get("/books?search=DEEP").json()["items"][0]["id"] == 2


def test_read_and_missing_book(load_tutorial):
    client = TestClient(load_tutorial("01-http-and-routing").app)
    response = client.get("/books/1")
    assert response.headers["x-lesson"] == "routing"
    assert response.json()["id"] == 1
    assert client.get("/books/999").status_code == 404


def test_invalid_path_and_query_parameters(load_tutorial):
    client = TestClient(load_tutorial("01-http-and-routing").app)
    assert client.get("/books/abc").status_code == 422
    assert client.get("/books?search=x").status_code == 422


def test_post_method(load_tutorial):
    client = TestClient(load_tutorial("01-http-and-routing").app)
    response = client.post("/echo?message=hello")
    assert response.status_code == 201
    assert response.json() == {"received": "hello"}
