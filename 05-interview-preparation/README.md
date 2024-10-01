# Backend Software Engineering — Interview Preparation (2024)

This folder is for practising backend interviews **by writing code**, not only memorising answers. It is one section of the 2024 `backend-software-engineering` collection.

I kept the examples small enough to explain on a whiteboard, but added real backend edge cases: retries, data races, SQL transactions, pagination, webhook security, and failed background jobs.

> **Scope:** These are learning and interview-practice implementations, **not** deployed production services. In particular, the rate limiter and webhook replay store live in one process; the job runner is a single-worker demo; and the payment example never moves real money.

## Inside this folder

```text
README.md
RUN_ON_WINDOWS.md
requirements-dev.txt
pytest.ini
questions/
  01-http-apis.md
  02-databases-transactions.md
  03-auth-security.md
  04-concurrency-performance.md
  05-testing-debugging.md
  06-architecture-tradeoffs.md
hands_on/
  idempotent_payments.py
  sliding_window_rate_limit.py
  concurrent_stock_orders.py
  audit_log_pagination.py
  signed_webhook.py
  retry_job_queue.py
  README.md
  requests.http
system_design/
  01-url-shortener.md
  02-order-booking-service.md
  03-notification-system.md
mock_interviews/
  01-backend-screen.md
  02-live-coding.md
  03-project-walkthrough.md
tests/
  test_interview_apps.py
```

## Technical baseline

- **Collection year:** 2024. The examples target **Python 3.11**, FastAPI and related versions available by the end of 2024. No 2025/2026-only APIs are necessary.
- `sqlite3`, `hashlib`, `hmac`, locks, and queues from the Python standard library handle most of the logic. This makes it easier to talk through *why* the code behaves the way it does.
- Dependency versions are specified in `requirements-dev.txt`. Test results below refer to the available test environment, not a verified run against every 2024-pinned library version.

## Run and test

From this folder:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Run one practice API at a time:

```powershell
python -m uvicorn hands_on.idempotent_payments:app --reload
```

Go to <http://127.0.0.1:8000/docs> and try it using Swagger UI. For other APIs replace the module name with any filename below. **Do not run the other services on the same port at the same time.**

## Practical coding rounds

| Round | Working example | Interview question to answer |
|---|---|---|
| 01 | `idempotent_payments.py` | What happens when the client retries POST after a timeout? |
| 02 | `sliding_window_rate_limit.py` | How do you limit requests without unfairly blocking other API keys? |
| 03 | `concurrent_stock_orders.py` | How can two customers buying the last item avoid overselling? |
| 04 | `audit_log_pagination.py` | How do you add filtering, stable sorting and bounded result sizes? |
| 05 | `signed_webhook.py` | How can a service reject forged and replayed callbacks? |
| 06 | `retry_job_queue.py` | What should happen after a background task fails repeatedly? |

**Suggested practice:** Read the prompt in `hands_on/README.md` before opening the `.py` file. Try to design the endpoint and data structure yourself, then compare the included implementation. After reading the tests, add one more edge case.

## Interview workflow

1. Start with `questions/01-http-apis.md`, then continue through the question bank.
2. Work through one hands-on round and say your reasoning out loud: **requirements → design → code → tests → tradeoffs**.
3. Pick a system-design prompt and draw an architecture. Include a database schema, API endpoints, and failure modes.
4. Use the mock interviews to time yourself and track where you get stuck. It's fine to say you don't know a detail—explain how you would verify it.
5. Use `mock_interviews/03-project-walkthrough.md` for a project explanation based on **work actually built and tested**.

## Checks and limitations

Test coverage includes expected responses plus negative tests (invalid data, duplicate requests, missing records, signature failures, retries and concurrency). Tests are intentionally self-contained; there is no cloud account or paid API requirement.

Before treating any example as production-ready, add real authentication/authorisation, audit-grade logging, secrets management, operational monitoring, dependency security reviews, and production-database tests. Specific missing pieces are discussed in each exercise.

## Attribution and learning

This folder uses common backend patterns implemented as original teaching examples. If code is later imported from another open-source project, preserve the source's license and attribution. Dates in the folder describe the **2024 learning collection**, not historical Git commit dates.
