# Case 03 — API traffic spike and overload protection

## Scenario (invented)

Our small API suddenly receives many requests. If all work is admitted, queues grow and the service may get slower for everyone. In this exercise I wanted to try two separate controls: limit the **rate per client** and cap the amount of work running **at the same time**.

## What I implemented

- A Python **token-bucket rate limiter** (per client key)
- A nonblocking **concurrency bulkhead** to reject excess in-flight work
- `GET /work` (simulate a small job), `GET /health`, and `GET /metrics`
- `429 Too Many Requests` or `503 Service Unavailable` with `Retry-After`
- A synthetic CSV request trace and an actual replay script
- Fake-clock tests, isolation tests, and a concurrency test

## Run

```powershell
python -m uvicorn traffic_spike.app:app --reload
```

In a second PowerShell terminal (from this same folder):

```powershell
python tools/replay_traffic.py
```

Try changing the configuration before starting the server:

```powershell
$env:BURST_CAPACITY='3'
$env:REFILL_RATE='1'
$env:MAX_PARALLEL='1'
python -m uvicorn traffic_spike.app:app --reload
```

The CSV values are synthetic request labels. The script prints counts from the **actual run**; exact totals depend on timing, machine load, and environment.

## What I learned

Rate limiting and concurrency limits solve different issues: rate limiting rejects bursts based on a time budget; a bulkhead caps simultaneous expensive operations. A request rejected due to worker capacity still consumed a rate-limit token in this simple design. This tradeoff is intentional and documented.

## Limits

This limiter is **per Python process**, keeps in-memory state without eviction, and trusts a caller-supplied test header. It is **not safe as a distributed production rate limiter**. In a real deployment, use authenticated client identity, bounded state or a centralized service, proper observability, and load tests before selecting limits.

See `docs/incident-review.md` and `docs/capacity-decisions.md`.
