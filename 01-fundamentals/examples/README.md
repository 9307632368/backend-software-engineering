# Practical Backend Examples — 2024 Track

This is the second part of my Backend Software Engineering fundamentals folder. The [tutorials](../tutorials/README.md) explain the core ideas; these examples put those ideas into small, working APIs.

They are **learning projects**, not claimed production-ready services. I kept the code short enough to follow and included tests so that changing an endpoint is less risky.

| Order | Folder | Key implementation | External service |
|---|---|---|---|
| 01 | [User registration and login](01-user-registration-login/) | Salted password hashes and login checks | None |
| 02 | [File upload service](02-file-upload-service/) | Streaming upload, size checks and downloads | None |
| 03 | [Database relationships](03-database-relationships/) | Users, products, orders and SQLAlchemy relations | SQLite (local) |
| 04 | [JWT authentication](04-jwt-authentication/) | Token signing, expiry and protected route | None |
| 05 | [Email notifications](05-email-notification-service/) | Template messages and background tasks | Demo sender (no real email) |
| 06 | [Redis caching](06-redis-caching/) | Cache hits, TTL and invalidation | Redis + Docker Compose |
| 07 | [Logging and configuration](07-logging-configuration/) | Structured logs and environment settings | None |
| 08 | [API testing and docs](08-api-testing-documentation/) | Typed responses and OpenAPI | None |

## Setup (Windows PowerShell)

From the `backend-software-engineering` repository root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Run any example from **its own directory**, not from the repository root:

```powershell
cd 01-fundamentals/examples/01-user-registration-login
python -m uvicorn app:app --reload
```

Visit <http://127.0.0.1:8000/docs>. Stop with `Ctrl+C` and return to the repository root before switching examples.

The Redis example needs Docker Compose, and the JWT example needs a signing key; those READMEs explain the extra commands.

## How the versions were chosen

This track uses Python **3.11** (3.12 is also suitable) and [versions that existed in 2024](2024-package-notes.md). Dates are curriculum labels only. No past commit history is being claimed.

Historical dependencies can contain vulnerabilities discovered later. Upgrade and re-test before putting any of these services on the internet.

## Practice ideas

1. Add tests for invalid requests before changing the implementation.
2. Replace in-memory storage with a database and compare the two designs.
3. Add a simple architecture diagram showing a client, the API, and the data store.
4. Add authentication before exposing uploads, messages, or personal data to other users.
5. Read the production limitations in each folder before adapting an example.

## Status

- 8 runnable FastAPI examples included.
- Unit/API tests included under `/tests` (they do not need Redis running).
- Docker Redis connectivity and outgoing email delivery have **not** been validated as deployed services.
