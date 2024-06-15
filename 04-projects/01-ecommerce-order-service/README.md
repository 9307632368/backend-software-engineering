# E-Commerce Order Management API (2024 backend project)

I wanted to learn how an online store keeps orders and stock consistent, especially when someone refreshes a checkout request or multiple users try to buy the last item. I kept the payment side out of scope, because I don't want to pretend a real payment gateway was implemented.

### Features actually implemented
- Customer signup/login; admin-only product creation and inventory replenishment.
- Multi-item checkout, stock decrement using a conditional SQL UPDATE, and one database transaction.
- Retry protection with a per-customer `Idempotency-Key` header; order lists, cancellation with stock restore, staff fulfillment.
- Price snapshots in **integer cents** rather than floating-point money; audit trail for order status changes.
- Dockerfile, Compose, HTTP request examples, API documentation and isolated tests.


## What I implemented

This project is a practical backend exercise built around a realistic business workflow. It is intended to be readable for someone learning backend engineering: small modules, explicit status codes, and tests for the cases that commonly break.

The business rules are implemented locally; third-party payment, email, and SMS providers are **not** integrated. `Base.metadata.create_all()` is used to keep setup simple. A real deployment should use Alembic migrations, Postgres, secrets management, audit retention, access reviews, and load testing.

## Setup (Windows PowerShell)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m app.bootstrap_admin
python -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs for Swagger UI. To authenticate, call `/auth/login`, then use the `Authorize` control with the returned bearer token. A customer account can be created using `/auth/register`; it cannot choose its role. Staff/admin accounts require the interactive bootstrap or a protected user-management process.

```powershell
$env:JWT_SECRET = "replace-with-a-long-random-secret-before-deploy"
$env:DATABASE_URL = "sqlite:///./app.db"
```

## Design decisions and boundaries

- Passwords use salted PBKDF2-HMAC-SHA256, and JWT access tokens expire after four hours. The demo lacks refresh tokens, password resets, session revocation and brute-force controls.
- APIs enforce role and ownership checks in the backend, not just in the frontend.
- SQLite is for repeatable local experiments; production-grade deployments need a supported transactional database, migrations and infrastructure hardening.
- This is an educational, functioning project with production-inspired patterns, **not** a claim of deployment at enterprise scale.
- The **2024** label identifies the target technology era, not a statement about when the code was originally authored or published.

### Try this workflow
1. `python -m app.bootstrap_admin`, then sign in using `/auth/login`.
2. Admin adds a product using `POST /products` (price in cents, e.g. 1250 for 12.50).
3. Customer signs up, logs in, and sends `POST /orders` with `Idempotency-Key: checkout-12345678`.
4. Retry the same request/key. Observe that the same order is returned.
5. Cancel it once; stock is restored. Cancelling again returns HTTP 409.

### Things I would improve
Use real PostgreSQL isolation, payment integration with an outbox, and a stored request fingerprint for strict idempotency (currently the same key returns the first order regardless of a different body). Add Alembic, OpenTelemetry, load tests, refunds and shipment states. Concurrent tests on SQLite do not establish production-scale throughput.

See `docs/architecture.md` and `docs/requests.http`.
