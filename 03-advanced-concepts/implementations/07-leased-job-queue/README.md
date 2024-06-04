# 07. Job queue with worker leases

A background worker can stop in the middle of a task. I wanted a job to be recoverable without assuming it runs exactly once.

The demo stores jobs in SQLite. Workers **claim** pending jobs, receive a private lease token, and must acknowledge completion before the lease expires. If a worker fails or disappears, the job can be retried; after a maximum number of attempts it becomes `dead`.

**Hands-on:**

1. `POST /jobs` with `{"task":"send-receipt", "data":"order-12"}`.
2. `POST /worker/claim`; save the returned `lease_token`.
3. `POST /worker/{id}/complete` with that token. Compare behavior with a wrong token.
4. Try `POST /worker/{id}/fail` until the job reaches the dead state.

Run `python -m uvicorn app:app --reload` and `python -m pytest -q tests`.

**Important limitation:** there is no real background worker loop here; API endpoints model worker actions for study. The job queue is **at-least-once**, not exactly-once. Workers must make side effects idempotent; heartbeats, per-task authorization, backoff, scheduling and real broker infrastructure are not included. `/worker/*` endpoints must be restricted to trusted workers in production.
