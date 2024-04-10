# 06 — Dependencies and Services: Shipping Quotes

An API becomes hard to change when calculation logic is mixed into the HTTP route. This lesson moves the shipping formula into `PricingService` and injects it using `Depends`.

## The flow

`GET /shipping/quote` → validate query parameters → request `PricingService` → calculate price → return structured JSON.

Formula (values in paise):

```text
5000 base + 150 × distance_km + 1200 × ceil(weight_grams / 1000)
+ 2500 if priority shipping is selected
```

A package travelling 10 km and weighing 1500 grams costs 5000 + 1500 + 2400 = **8900 paise (₹89)**. For a priority delivery, add 2500 paise.

The tests also **override** `get_pricing_service()` with a fake class. That verifies the route can be tested without relying on the original price calculation.

## Run

```powershell
python -m uvicorn app:app --reload
Invoke-RestMethod 'http://127.0.0.1:8000/shipping/quote?distance_km=10&weight_grams=1500'
```

## Exercises

1. Add a surcharge for packages heavier than 10 kg.
2. Write a unit test for the exact cost at 1, 1000 and 1001 grams.
3. Add a second service for international delivery and choose it using a request parameter.

**Limit:** Rates are invented for practice. This isn't a real courier's pricing or payment system.
