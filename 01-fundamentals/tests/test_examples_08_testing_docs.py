from fastapi.testclient import TestClient

def test_book_catalog_and_errors(load_example):
    module = load_example("08-api-testing-documentation")
    with TestClient(module.create_app()) as api:
        assert api.get("/books").json() == {"items": [], "count": 0}
        assert api.get("/books/42").status_code == 404
        book = api.post("/books", json={"title": "Backend Basics", "author": "A Student"})
        assert book.status_code == 201
        assert book.json()["id"] == 1
        assert api.get("/books/1").json()["title"] == "Backend Basics"
        assert api.get("/books?limit=0").status_code == 422
        assert api.delete("/books/1").status_code == 204
        assert api.delete("/books/1").status_code == 404

def test_openapi_spec_has_documented_models(load_example):
    module = load_example("08-api-testing-documentation")
    with TestClient(module.create_app()) as api:
        spec = api.get("/openapi.json").json()
        assert spec["info"]["title"] == "Book Catalog API"
        assert "/books" in spec["paths"]
        assert "BookCreate" in spec["components"]["schemas"]
        assert api.get("/docs").status_code == 200
