# Customer Support Ticketing Platform (2024 backend project)

This started as a question: how does a support agent follow a ticket without allowing another customer to see it? I wrote a small service with the important workflow rules in the API instead of only making a ticket CRUD demo.

### What it does
- Customer registration and login, authenticated ticket creation and status tracking.
- Agent/admin assignment of tickets, explicit status transitions and rejection of invalid transitions.
- Separate public replies and **internal staff-only notes**, including read-side filtering.
- Ticket activity log for staff, ownership checks, pagination and input validation.
- Automated tests for cross-user access, private comments, role checks, status flow and invalid input.


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
1. Register a customer, then create a ticket with `POST /tickets`.
2. Bootstrap an admin using `python -m app.bootstrap_admin`. Log in as admin and use `POST /staff/agents` to create an agent account.
3. Log in as the agent and assign the ticket using `PATCH /tickets/{id}/assign`.
4. Add an internal note and a public reply; confirm the customer can read only the public reply.
5. Move the ticket `open` → `in_progress` → `resolved`; inspect audit events.

### What is not included
Real email integrations, automatic SLA enforcement, escalation scheduling, attachments, tenant-level data isolation, and an end-user frontend. Ticket status changes should use optimistic locking if many agents can edit a ticket at once. These are good follow-up tasks.
