# 01. Circuit breaker and retries

**Problem I wanted to reproduce:** What happens when a supplier API fails repeatedly and our service keeps calling it?

I made a fake supplier that intentionally fails. The quote endpoint tries at most twice. After two failed requests the breaker opens, and the service stops calling the supplier until the cooldown ends. One request can test recovery in the half-open state.

Run `python -m uvicorn app:app --reload`, then `python -m pytest -q tests`.

Try changing `FakeSupplier(failures_left=3)` in `app = create_app(...)`, or change the cooldown. Watch `/health/supplier` while calling `GET /quotes/ABC`.

**What I learned:** a retry protects against transient failures, while a circuit breaker protects *our* service from an unhealthy downstream. This is a controlled in-process demo, not a distributed circuit breaker. I skipped waiting between retries for repeatable tests; a real service needs a backoff, jitter, request timeout and per-host metrics. Only retry operations that are safe to replay.
