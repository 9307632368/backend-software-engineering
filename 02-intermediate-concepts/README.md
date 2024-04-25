# 02 — Intermediate Backend Concepts (2024 collection)

This folder is the next step after `01-fundamentals`. I wanted each topic to be something I can **run**, **test**, and **change** instead of keeping notes only.

The projects here are small learning implementations, not production services. A few contain deliberate simplifications (for example local SQLite instead of PostgreSQL, local mock notifications, no external payment provider). Each README explains the trade-offs.

## Folder map

| Group | Folder | What I practiced |
| --- | --- | --- |
| Tutorials | `01-dependencies-and-settings` | Dependencies, configuration, API keys |
| Tutorials | `02-database-transactions` | SQLAlchemy relationships, transactions |
| Tutorials | `03-async-io-workloads` | Concurrency for I/O, timeouts |
| Tutorials | `04-request-response-contracts` | Pydantic nested models, response contracts |
| Practical examples | `05-idempotent-checkout` | Safe repeat requests and business conflicts |
| Practical examples | `06-webhook-verification` | HMAC verification and duplicate events |
| Practical examples | `07-keyset-pagination` | Stable cursor pagination, filters |
| Mini projects | `08-support-ticket-api` | Ticket lifecycle, audit logs, authorization |
| Mini projects | `09-inventory-order-workflow` | Stock reservation, confirm/cancel, atomicity |

## How to run (Windows PowerShell)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-2024.txt
python check_all.py

cd tutorials/01-dependencies-and-settings
python -m uvicorn app:app --reload
# browser: http://127.0.0.1:8000/docs
```

All nine examples have their own README, `app.py`, `requests.http` and `tests/` so they can be studied separately. Change into a project's directory before starting its server or running its tests.

## Versions and honesty note

- Target stack: **Python 3.11**, FastAPI **0.115.6**, Pydantic **2.10.4**, Uvicorn **0.32.1**, SQLAlchemy **2.0.36**, httpx **0.28.1**, pytest **8.3.4** (releases available by the end of 2024).
- **2024 labels classify the portfolio collection**, not the dates of the commits or the original authorship history.
- The automated tests for this collection were run on a newer preinstalled environment; exact pinned-version compatibility should also be checked on a Python 3.11 installation.
- Do not commit real API keys or credentials. Examples use development placeholders and `.env.example` only.

## What I would improve next

PostgreSQL migrations; central authentication; rate limits; a proper message broker; distributed tracing; load testing; deployment environments; and finer-grained security controls. The advanced-project sections will cover some of these.
