# 06. Token-bucket rate limiting

I wanted to implement rate limiting instead of only adding a library. A bucket has a capacity (burst size), and tokens slowly refill over time. Every accepted request costs one token. When empty, the server responds **429** with `Retry-After`.

Run `python -m uvicorn app:app --reload`. Try calling `GET /reports` four times with the `X-API-Key: demo-alpha` header. Then wait a couple of seconds and try again. Tests use a fake clock so they do not sleep.

**Limits:** API keys here are public demo strings, not real credentials. The state is in-process memory; each replica would independently allow a burst. A production quota needs an atomic shared backend (e.g. Redis/Lua), identity verification, key eviction, and protection against abusive memory growth.
