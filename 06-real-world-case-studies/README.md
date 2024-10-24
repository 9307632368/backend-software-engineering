# Real-World Backend Case Studies (2024 learning collection)

This folder is the **case-studies** part of my Backend Software Engineering repository. I wanted to go beyond a list of API endpoints and understand what breaks when a service has retries, concurrent requests, or unexpected traffic.

> **Important:** All three incidents are **fictional, locally reproducible simulations**. They are not incidents I handled at a company. The "2024" label describes the selected technology period and learning collection; it is not a claim that the commits were made in 2024.

## What I implemented

| Case | Realistic failure | Implementation | Tests |
| --- | --- | --- | --- |
| [01 Flash sale overselling](01-flash-sale-overselling/) | Many buyers attempt to buy limited stock | SQLite transactions, conditional stock updates, and request idempotency | Concurrency and duplicate requests |
| [02 Payment webhook retries](02-payment-webhook-retries/) | Webhooks arrive twice, late, or before a payment is visible | HMAC verification, event deduplication, state machine, and reconciliation | Replays, signatures, and out-of-order delivery |
| [03 API traffic spike](03-api-traffic-spike/) | A small service receives an unexpected burst | Token-bucket limiting, nonblocking bulkhead, and traffic replay | Rate limits, fake clock, and overload |

## Set up on Windows (PowerShell)

Run these commands from **this folder** after extracting it into `06-real-world-case-studies/`.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-2024.txt
python -m pytest -q
```

Run a case from its own folder, for example:

```powershell
cd 01-flash-sale-overselling
python -m flash_sale.seed
python -m uvicorn flash_sale.app:app --reload
```

The browser API docs are at `http://127.0.0.1:8000/docs`.

## How to study the cases

1. Read the scenario in each case README and the short incident note in `docs/`.
2. Run the application, make the example requests, and run the tests.
3. Make a small change (for example, remove idempotency in a separate copy) and see what breaks.
4. Read the tradeoffs section. These are deliberately small study projects, not complete production systems.

Each project is standalone. Run them one at a time because they use port 8000 by default.

## Security and scope

- Payment credentials in `.env.example` are **local demo placeholders**; replace them for testing and do not publish real secrets.
- SQLite is a good way to inspect transactions but not the target database for a high-volume distributed service.
- No real payments, purchases, customer data, or external services are involved.
- API responses and traffic traces use invented data.
- We do not claim performance improvements or production readiness without measured benchmarks.

## Dependencies

`requirements-2024.txt` pins versions released by the end of 2024. The automated tests are run in the available environment; exact historical pins must also be verified separately on your own machine.
