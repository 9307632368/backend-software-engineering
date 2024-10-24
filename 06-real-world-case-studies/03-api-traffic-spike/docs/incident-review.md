# API traffic spike — simulated incident

## Symptoms
- Slow responses under a traffic burst
- Server threads stay busy and new requests wait
- One noisy client impacts other clients

## Possible root causes
- No admission control
- Too many operations in flight
- Work queued faster than it completes

## Countermeasures in this example
- Per-client token bucket; excess returns HTTP `429`
- Nonblocking semaphore limiting concurrent work; full capacity returns HTTP `503`
- A health endpoint, basic counters, and a reproducible synthetic trace

## Testing
The code includes fake-clock unit tests for replenishment and a blocked-worker test for the `503` path. The replay script outputs **measured counts per run**, not invented latency improvement claims.

## Follow-up for a real system
- Measure p50/p95/p99 latency and throughput under controlled load.
- Move quotas to a centralized rate limit service if there are several app workers.
- Replace self-declared client labels with authenticated identity.
- Expose metrics securely through an established monitoring stack.
- Add circuit breakers, backoff with jitter, and appropriately bounded queues.
