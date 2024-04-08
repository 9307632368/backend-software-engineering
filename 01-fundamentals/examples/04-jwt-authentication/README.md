# 04 — JWT authentication

**Track:** Backend Software Engineering / 2024 / Fundamentals / Practical Examples

## What I am practicing

Issue a signed token on login and use it to access a protected route.

2024-level concepts: bearer auth, HS256 tokens, subject/expiry claims, protected endpoints.

## Run it

Install the pinned requirements once from the **main repository root** with `python -m pip install -r requirements-dev.txt`. Then move into this folder and run:

```powershell
$env:JWT_SECRET_KEY = "replace-this-with-a-random-value-of-32-or-more-chars"
```

```powershell
python -m uvicorn app:app --reload
```

Open <http://127.0.0.1:8000/docs>. `requests.http` has sample requests for VS Code REST Client.

## Try it yourself

Set JWT_SECRET_KEY to a local random value of 32+ characters. Register, request a token, and call /me with Authorization: Bearer <token>.

## How it can be improved

This is a lesson, not a full identity provider. No refresh tokens, account recovery, token revocation, account lockout or HTTPS configuration.

## Related files

- `app.py` — runnable service, with comments at the important steps.
- `requests.http` — test requests.
- `/tests/test_examples_04_*.py` — automated tests, located at the repository root.

**Note:** The year is a curriculum label. It does not mean the code was originally committed in 2024.
