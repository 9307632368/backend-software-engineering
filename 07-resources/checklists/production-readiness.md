# Production readiness: things the learning sample does NOT solve

**Warning:** Passing a test suite is not equal to being production-ready.

- [ ] Persistent DB and tested migrations rather than in-memory state.
- [ ] Robust authorization on every protected object.
- [ ] Managed secrets, TLS and secured infrastructure.
- [ ] Bounded request size, timeouts, retries and idempotency.
- [ ] DB connection limits and transaction/concurrency tests.
- [ ] Structured logs, metrics, alerting and meaningful health checks.
- [ ] Backup and restore tested; incident response procedure written.
- [ ] CI gates, dependency/security scans and rollout/rollback plan.
- [ ] Load tested under representative hardware and traffic.
- [ ] Privacy, retention and regulatory requirements evaluated for the actual product.

If a project only includes the basics, explain that clearly in its README.
