# 07 — Logging and configuration

**Track:** Backend Software Engineering / 2024 / Fundamentals / Practical Examples

## What I am practicing

Read settings from environment variables and log structured metadata for every request.

2024-level concepts: middleware, JSON logs, request IDs, settings dataclasses, response codes.

## Run it

Install the pinned requirements once from the **main repository root** with `python -m pip install -r requirements-dev.txt`. Then move into this folder and run:

```powershell
python -m uvicorn app:app --reload
```

Open <http://127.0.0.1:8000/docs>. `requests.http` has sample requests for VS Code REST Client.

## Try it yourself

Start the service and request /health. Look at the terminal log line and the X-Request-ID response header. Change APP_ENV and MAX_ITEMS.

## How it can be improved

This example intentionally skips request bodies and query strings to reduce accidental leakage. Production needs centralized log collection, robust tracing, and consistent exception responses.

## Related files

- `app.py` — runnable service, with comments at the important steps.
- `requests.http` — test requests.
- `/tests/test_examples_07_*.py` — automated tests, located at the repository root.

**Note:** The year is a curriculum label. It does not mean the code was originally committed in 2024.
