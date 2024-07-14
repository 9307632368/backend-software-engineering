# Appointment Booking Service (2024 backend project)

The difficult part of appointment booking is not showing a calendar: it is preventing two people from reserving the same slot. I made an API that checks the booking condition inside an SQL UPDATE and rejects another request if the slot is already taken.

### What is implemented
- Admin-configured services and 30-minute UTC appointment slots.
- Customer authentication with short-lived JWT tokens and ownership-protected bookings.
- Transactional slot claiming (`UPDATE ... WHERE booked = false`), idempotency keys and cancellation that releases a future slot.
- Date validation, duplicate slot prevention, booking history, API documentation and tests.


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

### Manual workflow
1. Create an admin account with `python -m app.bootstrap_admin` and log in.
2. Create a service via `POST /services`.
3. Create a future slot via `POST /services/{id}/slots` using an ISO-8601 UTC time on a half-hour boundary.
4. Register two customers. Both attempt to book the same slot. One succeeds and the other gets HTTP 409.
5. Cancel the original booking. Now another customer can reserve that released slot.

### Limitations to study next
No payment gateway, external calendar integration, reminder service or daylight-saving handling of local calendars. All dates are stored as canonical UTC strings. The service assumes fixed 30-minute appointments, not variable durations. Real high-concurrency deployments should use PostgreSQL with migrations and sustained concurrency tests. A reused idempotency key returns the first booking even with a changed request body; strict retry semantics need a request fingerprint.
