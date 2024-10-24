# Case 01 — Flash sale overselling

## Scenario (invented)

An online store has only 5 headsets. Twelve customers click **Buy** almost at the same time. A second problem appears when a client times out and retries its request. If the code simply reads stock, checks it, and subtracts stock later, multiple requests can observe the same old quantity and oversell.

## What I built

- `GET /products/{sku}` to inspect remaining stock
- `POST /orders` with an `Idempotency-Key` header
- `GET /orders/{order_id}`
- SQLite schema with unique client/request keys, writer transactions, and conditional stock updates
- Concurrent-buyer tests using multiple connections

## Try it

From this folder:

```powershell
python -m flash_sale.seed
python -m uvicorn flash_sale.app:app --reload
```

In a second PowerShell window:

```powershell
$body = '{"client_id":"buyer1","sku":"SKU-HEADSET","quantity":1}'
Invoke-RestMethod -Uri http://127.0.0.1:8000/orders -Method Post -ContentType application/json -Headers @{'Idempotency-Key'='buyer1-order-001'} -Body $body
Invoke-RestMethod http://127.0.0.1:8000/products/SKU-HEADSET
```

Repeat with the *same* key to see the replay. Try the same key with a different quantity; the API returns `409`.

## Lessons I wanted to learn

- Two operations that look correct individually can fail when requests overlap.
- Idempotency prevents client retries from placing the same order twice.
- Amounts are stored in **integer cents**, not floating-point numbers.
- A transaction controls stock and order creation as one unit.

Read `docs/incident-review.md` and `docs/design-decisions.md` before extending the system.

## Limitations

This does **not** charge real cards, implement product reservations with expiration, authorize users, or use a distributed database. The `client_id` comes from input for demonstration only; in production it must come from authenticated identity. SQLite allows one writer at a time: the same design idea would need to be adapted and load-tested for PostgreSQL or another production database.
