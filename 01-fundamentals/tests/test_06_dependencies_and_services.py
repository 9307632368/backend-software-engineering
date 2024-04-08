from fastapi.testclient import TestClient


def test_quote_calculation(load_tutorial):
    client = TestClient(load_tutorial("06-dependencies-and-services").app)
    res = client.get("/shipping/quote?distance_km=10&weight_grams=1500")
    assert res.status_code == 200
    assert res.json()["total_paise"] == 8900


def test_priority_adds_surcharge(load_tutorial):
    client = TestClient(load_tutorial("06-dependencies-and-services").app)
    res = client.get("/shipping/quote?distance_km=10&weight_grams=1500&priority=true")
    assert res.json()["total_paise"] == 11400


def test_weight_rounds_to_next_kilogram(load_tutorial):
    service = load_tutorial("06-dependencies-and-services").PricingService()
    assert service.calculate_paise(1, 1001, False) == 7550
    assert service.calculate_paise(1, 1000, False) == 6350


def test_invalid_input_is_422(load_tutorial):
    client = TestClient(load_tutorial("06-dependencies-and-services").app)
    assert client.get("/shipping/quote?distance_km=0&weight_grams=1000").status_code == 422


def test_dependency_override(load_tutorial):
    module = load_tutorial("06-dependencies-and-services")
    class FixedService:
        def calculate_paise(self, distance_km, weight_grams, priority):
            return 12345
    module.app.dependency_overrides[module.get_pricing_service] = lambda: FixedService()
    try:
        client = TestClient(module.app)
        assert client.get("/shipping/quote?distance_km=2&weight_grams=500").json()["total_paise"] == 12345
    finally:
        module.app.dependency_overrides.clear()
