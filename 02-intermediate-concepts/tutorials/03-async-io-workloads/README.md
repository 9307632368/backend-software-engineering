# Tutorial 03 — Async for I/O Workloads

I compared sequential I/O waiting with `asyncio.gather`, then added a timeout using `wait_for`. The project uses two **simulated upstream services**, so it is easy to run offline.

Launch: `python -m uvicorn app:app --reload`. Send `POST /availability` with `{"sku":"BOOK-10"}`. Try `timeout_ms: 1` and see what happens.

**Note:** `async` does not make CPU-heavy work faster by itself. For expensive computation, explore processes/workers. For production upstream calls, use an async HTTP client with explicit connect/read timeouts, retries, and circuit breakers.

**Practice:** record elapsed timings and compare concurrent vs sequential requests.
