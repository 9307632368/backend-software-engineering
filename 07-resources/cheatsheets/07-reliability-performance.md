# Reliability and performance quick notes

## Timeout, retry, backoff

Set a finite timeout for network calls. Retry only safe or idempotent operations, with exponential backoff and jitter. A retry without idempotency can create duplicate orders or charges.

## Small patterns

| Problem | Approach | Watch out for |
|---|---|---|
| Duplicate webhook | Verified signature + durable event ID | Checking the ID without atomic insert |
| Traffic spike | Per-client limit + bounded concurrency | Denying all clients behind one shared IP |
| Slow repeated query | Cache with explicit TTL | Stale data, invalidation |
| Transient worker failure | Durable queue + bounded retries | Poison messages, retry storms |
| Last stock item | Conditional update / transaction | Read-then-write race |
| Downstream unavailable | Timeout + fallback / circuit breaker | Silent data loss |

## Performance notes

Measure before changing code. For a new endpoint, record dataset size, concurrency level, hardware and actual measurement command. Avoid reporting synthetic numbers as real production benchmarks.
