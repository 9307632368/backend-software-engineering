from fastapi.testclient import TestClient


def test_default_page(load_tutorial):
    client = TestClient(load_tutorial("07-pagination-and-filtering").app)
    result = client.get("/catalog").json()
    assert result["total"] == 6
    assert len(result["items"]) == 3
    assert result["has_more"] is True


def test_second_page(load_tutorial):
    client = TestClient(load_tutorial("07-pagination-and-filtering").app)
    result = client.get("/catalog?limit=2&offset=2").json()
    assert [item["id"] for item in result["items"]] == [3, 4]


def test_category_filter_and_sort(load_tutorial):
    client = TestClient(load_tutorial("07-pagination-and-filtering").app)
    result = client.get("/catalog?category=accessories&sort_by=price_paise&order=desc").json()
    assert result["total"] == 3
    assert [p["name"] for p in result["items"]] == ["Keyboard", "Wireless Mouse", "USB-C Cable"]


def test_search_is_case_insensitive(load_tutorial):
    client = TestClient(load_tutorial("07-pagination-and-filtering").app)
    result = client.get("/catalog?search=DESK").json()
    assert result["total"] == 1
    assert result["items"][0]["name"] == "Desk Lamp"


def test_empty_page_has_no_more(load_tutorial):
    client = TestClient(load_tutorial("07-pagination-and-filtering").app)
    result = client.get("/catalog?offset=100").json()
    assert result["items"] == []
    assert result["has_more"] is False


def test_invalid_sort_and_limit_return_422(load_tutorial):
    client = TestClient(load_tutorial("07-pagination-and-filtering").app)
    assert client.get("/catalog?sort_by=internal_notes").status_code == 422
    assert client.get("/catalog?limit=10000").status_code == 422
