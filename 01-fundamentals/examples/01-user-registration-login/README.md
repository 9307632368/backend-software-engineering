# 01 — Registration and login

**Track:** Backend Software Engineering / 2024 / Fundamentals / Practical Examples

## What I am practicing

Store new users without saving plain-text passwords.

2024-level concepts: POST routes, input validation, salts, PBKDF2, constant-time comparisons.

## Run it

Install the pinned requirements once from the **main repository root** with `python -m pip install -r requirements-dev.txt`. Then move into this folder and run:

```powershell
python -m uvicorn app:app --reload
```

Open <http://127.0.0.1:8000/docs>. `requests.http` has sample requests for VS Code REST Client.

## Try it yourself

Register two accounts; try a repeated email, then a wrong password. Password hashes differ even for equal passwords.

### Why not store the original password?
A database leak should not immediately expose every user password. `hash_password` uses a fresh random salt and PBKDF2. `password_matches` compares hashes using `hmac.compare_digest`. This is a learning example; password storage for production needs a current security review.

## How it can be improved

The storage resets when the server restarts, there is no session or rate limiter, and a real product should use a maintained authentication framework and reviewed password-hashing scheme.

## Related files

- `app.py` — runnable service, with comments at the important steps.
- `requests.http` — test requests.
- `/tests/test_examples_01_*.py` — automated tests, located at the repository root.

**Note:** The year is a curriculum label. It does not mean the code was originally committed in 2024.
