# Mini Project 09 — Inventory and Order Workflow

In a stock system, a customer order must not automatically reduce physical stock before confirmation. I built a three-step flow: **reserve → confirm** or **reserve → cancel**.

## Endpoints

- `POST /products` — create catalog item with quantity and price
- `GET /products/{sku}` — stock, reserved, and available quantities
- `POST /orders` — reserve available stock without changing physical stock
- `GET /orders/{id}` — read an order
- `POST /orders/{id}/confirm` — consume stock and release the reservation
- `POST /orders/{id}/cancel` — release reserved quantity

SQLite `BEGIN IMMEDIATE` keeps the check and stock update together on this single-machine demo. Quantity conflicts return HTTP 409. Repeating confirm/cancel on a finalized order is rejected.

## Limits

There is **no account login or checkout payment**, and no automatic reservation expiry. SQLite's serialization helps locally but does not replace a production design for distributed ordering. Production code needs identity and authorization, inventory movement records, database migrations, idempotency, refunds, stock reconciliation, and observability.

**Practice:** add a reservation expiration task, an order event history, and tests for two competing requests.
