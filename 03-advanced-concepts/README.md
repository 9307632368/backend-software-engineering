# 03 — Advanced Backend Concepts | 2024 collection

I built these small services to understand the things that can go wrong *after* an API starts working: a slow downstream service, stale database updates, duplicate events, different tenants accessing the same tables, requests arriving too quickly, and jobs crashing midway.

Each topic has a running API, automated tests, sample requests, and notes on what I would change before deploying it. These are **advanced learning implementations**, not production-ready systems. The folder is deliberately standalone so it can be merged into `backend-software-engineering/03-advanced-concepts/`.

| Path | Implementation | Main idea |
| --- | --- | --- |
| `tutorials/01-circuit-breaker-retry/` | Product quote API with fake supplier | Fail fast when the dependency keeps failing |
| `tutorials/02-optimistic-locking/` | Stock updates in SQLite | Avoid lost updates with a version column |
| `tutorials/03-transactional-outbox/` | Order API + delivery worker | Save business record and outgoing event together |
| `system-design/04-url-shortener/` | Link creation + redirect + statistics | Data model, capacity assumptions, collision handling |
| `system-design/05-multi-tenant-reporting/` | Isolated tenant sales reports | Tenant boundary and query-level isolation |
| `implementations/06-token-bucket-rate-limiter/` | API-key-based token bucket | Bounded bursts and 429 replies |
| `implementations/07-leased-job-queue/` | SQLite worker queue | Retries, leases, dead-letter state |
| `implementations/08-api-observability/` | Request IDs, JSON logs, metrics | Debugging and basic operational visibility |

## Run locally (PowerShell)

Tested with the Python packages available in the authoring environment. This collection targets **Python 3.11 + 2024 releases** of FastAPI, Pydantic, pytest, Uvicorn and httpx (see `requirements-2024.txt`). The exact pinned combination must also be verified on your own Python 3.11 environment.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-2024.txt
python check_all.py

cd tutorials/01-circuit-breaker-retry
python -m uvicorn app:app --reload
# open http://127.0.0.1:8000/docs
```

Each project has `requests.http` for the VS Code REST Client extension; the API Swagger UI also works.

## Why the design matters

- **Retries** only make sense for safe/idempotent operations, with bounded attempts and backoff in real systems.
- **Optimistic locking** protects concurrent changes even when multiple API workers exist.
- **Outbox** provides *at-least-once* publication, not exactly-once delivery; consumers must deduplicate.
- **Tenancy** must come from verified identity, not a client-supplied tenant ID.
- **Rate limiting** in-memory is one-process only. Distributed deployment needs a shared atomic store.
- **Queue workers** need idempotent tasks, because lease expiry can cause a second worker to run the same task.

## Boundaries of this portfolio example

No managed cloud services, no real email/payment integrations, no realistic load test and no production deployment is included here. Database examples use local SQLite for easier experimentation. Replace with PostgreSQL, migrations, observability infrastructure and security review before production use. The year is the collection label; it is **not** a claim of when the repository was originally committed.

## Exercise ideas

1. Add jittered exponential backoff to the circuit-breaker tutorial.
2. Run two stock updates in separate processes and inspect the conflict response.
3. Design a dead-letter/replay strategy for outbox events.
4. Estimate URL-shortener capacity for 100 million redirects/day.
5. Replace local API-key tenant mapping with OIDC-authenticated tenant claims.
6. Run Redis-based rate limits across three application replicas.
7. Make a queue task safely replayable with a durable business idempotency key.
8. Instrument database calls and downstream requests with OpenTelemetry.
