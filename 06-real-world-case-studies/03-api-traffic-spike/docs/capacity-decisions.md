# Capacity decisions and tradeoffs

| Decision | Benefit | Limitation |
| --- | --- | --- |
| Token bucket | Short bursts are allowed without granting unlimited requests | Requires an identity and cross-process coordination in distributed deployments |
| Nonblocking semaphore | The service rejects instead of accumulating unlimited work | Legitimate users can receive `503` at peak load |
| `Retry-After` | Clients have a hint about when to retry | Not a guarantee of capacity at that moment |
| `/metrics` counters | Makes local behavior visible | Not production-grade monitoring |

## Experiments to try

1. Reduce `BURST_CAPACITY` from 5 to 2. Replay the trace and compare actual HTTP counts.
2. Increase simulated work delay from 50ms to 500ms in `create_app()` and test concurrent callers.
3. Add a TTL eviction policy for clients that have been inactive for a long time.
4. Add a test that runs several Python processes and document why the in-memory quota is no longer globally enforced.
