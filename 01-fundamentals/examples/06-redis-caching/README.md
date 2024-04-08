# 06 — Redis caching

**Track:** Backend Software Engineering / 2024 / Fundamentals / Practical Examples

## What I am practicing

Keep product responses in a cache for 60 seconds and invalidate the cache after updates.

2024-level concepts: cache-aside, Redis GET/SETEX/DEL, TTL, cache invalidation.

## Run it

Install the pinned requirements once from the **main repository root** with `python -m pip install -r requirements-dev.txt`. Then move into this folder and run:

```powershell
docker compose up -d
```

```powershell
python -m uvicorn app:app --reload
```

Open <http://127.0.0.1:8000/docs>. `requests.http` has sample requests for VS Code REST Client.

## Try it yourself

Run Docker Compose in this example, request /products/1 twice, then update the price and request it again.

### Cache sequence
1. First GET: read a product from the in-memory store and write it to Redis.
2. Second GET: read it from Redis (`cache_hit: true`).
3. PUT: update the underlying value and delete the Redis key.
4. Next GET: fetch the new value and warm the cache again.

## How it can be improved

The product database is only a local dictionary, so it resets on restart; errors result in 503 instead of a database fallback. Avoid this simple strategy for sensitive or highly concurrent applications.

## Related files

- `app.py` — runnable service, with comments at the important steps.
- `requests.http` — test requests.
- `/tests/test_examples_06_*.py` — automated tests, located at the repository root.

**Note:** The year is a curriculum label. It does not mean the code was originally committed in 2024.
