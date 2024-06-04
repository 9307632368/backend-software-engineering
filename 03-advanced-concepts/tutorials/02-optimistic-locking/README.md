# 02. Optimistic concurrency in SQLite

**Bug to prevent:** two clients read stock=10, then both write a new value based on stale information. One update can silently overwrite the other.

I use `version` on each product. The API requires `expected_version` and performs `UPDATE ... WHERE version = ?`. Only one stale version can succeed. The losing request gets **409 Conflict** and should reload the record rather than blindly retry.

Try `GET /products/1`, then send the same expected version twice to `PATCH /products/1/stock`. The first should succeed; the second should receive 409. Tests also check persistence, missing products and stock going below zero.

Run `python -m uvicorn app:app --reload` and `python -m pytest -q tests`.

**Trade-off:** Works on a local database and keeps the change atomic, but a production database needs schema migrations, authorization and appropriate transaction isolation. Retrying a non-idempotent delta without re-reading can be dangerous.
