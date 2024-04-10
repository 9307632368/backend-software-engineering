# 05 — Email notification templates

**Track:** Backend Software Engineering / 2024 / Fundamentals / Practical Examples

## What I am practicing

Render messages from a couple of templates and queue them as background tasks.

2024-level concepts: BackgroundTasks, string templates, 202 responses, dependency injection.

## Run it

Install the pinned requirements once from the **main repository root** with `python -m pip install -r requirements-dev.txt`. Then move into this folder and run:

```powershell
python -m uvicorn app:app --reload
```

Open <http://127.0.0.1:8000/docs>. `requests.http` has sample requests for VS Code REST Client.

## Try it yourself

Post a welcome message and read /demo-outbox. Try the order message with and without an order_id.

## How it can be improved

No real email is sent. A production service would use SMTP/provider integration, retries, worker queues, authenticated admin tools, and a durable status store. Never expose demo-outbox publicly.

## Related files

- `app.py` — runnable service, with comments at the important steps.
- `requests.http` — test requests.
- `/tests/test_examples_05_*.py` — automated tests, located at the repository root.

**Note:** The year is a curriculum label. It does not mean the code was originally committed in 2024.
