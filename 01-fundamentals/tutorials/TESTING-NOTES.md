# Testing notes

I use three kinds of checks in this tutorial section:

| Check | Why I added it | Example |
|---|---|---|
| HTTP endpoint test | Verify the status code and JSON returned to a client | `/books/99` must return 404 |
| Business-logic test | Verify a calculation even without an HTTP request | 1001 g is billed as 2 kg |
| State/persistence test | Verify data doesn't leak between test cases and survives a restart when expected | Two separate SQLite app instances can read the same ticket DB |

## Running the tests

From the `backend-software-engineering` root:

```powershell
python -m pytest -q
python -m pytest tests/test_05_sqlite_persistence.py -v
```

FastAPI's `TestClient` runs the API inside the test process, so you **do not** start Uvicorn first. The SQLite tests use pytest's `tmp_path` fixture and never rely on the database you create while using the API manually.

### Why some tests create a new app

The in-memory CRUD and protected memo apps expose `create_app()`. Every call creates a separate store in memory. This lets one test create a note without accidentally influencing the next test. The SQLite app also supports `create_app(db_path=...)` so the database file is configurable.

### Manual testing vs automated testing

`requests.http` is useful while learning and debugging individual requests. Automated tests are useful when changing code later; they tell me if I accidentally broke something that worked before.

## Mistakes worth checking

- **404 vs 422:** `/books/999` is well-formed but doesn't exist (404); `/books/hello` has the wrong ID type (422).
- **201 vs 200:** Creating a note should return 201. Reading it should return 200.
- **204:** Successful delete should not return a JSON response body.
- **401 vs 403:** Invalid/missing key is 401; a valid read-only key trying to write is 403.
- **Transactions:** Commit changes to SQLite so later connections can read them.
- **Secrets:** Do not commit `.env` or put real API keys in `requests.http`.

## What I'd improve in the next section

Move repeated configuration into reusable modules, add logging and correlation IDs, use PostgreSQL and migration scripts, and add integration tests against disposable database services. Those changes belong in the larger application projects rather than making the fundamentals examples harder to follow.
