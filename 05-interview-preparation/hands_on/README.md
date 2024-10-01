# Hands-on backend interview rounds

These are six separate small FastAPI applications. **Read the problem first, try solving it, and only then compare with the Python file.** Each module exposes an `app` and a `create_app()` factory, which makes automated tests easier.

## 01 — Retry-safe payment simulation

**Prompt:** A customer submits a payment request. The server commits it, but the response is lost. The client sends the same request again. Avoid inserting a second payment and return the previous result. If the same idempotency key is reused with a different amount, return a conflict.

**What to think about:** integer smallest units (`paise`), unique constraints, transaction isolation, key scope, timeout retries, concurrency.

**Implementation:** `idempotent_payments.py` uses SQLite `BEGIN IMMEDIATE` plus a unique key. It is an interview exercise, not a real payment processor.

**Stretch task:** add a separate `status` column, track processing and failure states, and consider what should happen if an external payment gateway succeeds while the local transaction fails.

## 02 — Sliding-window rate limiter

**Prompt:** Allow a maximum number of requests per API key within a moving time window. Return HTTP 429 with `Retry-After` when over the limit.

**What to think about:** precise window boundaries, thread safety, testability using a fake clock, fair key separation.

**Implementation:** `sliding_window_rate_limit.py` uses a thread-safe deque per key. This does not share counters across multiple server processes.

**Stretch task:** explain how Redis `ZSET` or atomic Lua scripts would help multiple service replicas share a rate limit. Also consider eviction of inactive keys to prevent unbounded memory use.

## 03 — Overselling the last item

**Prompt:** Only one unit is available. Several customers submit an order at the same time. Exactly one should succeed.

**What to think about:** race conditions, read-modify-write, transactions, atomic SQL updates, lock contention, rollback.

**Implementation:** `concurrent_stock_orders.py` uses `UPDATE ... WHERE available >= quantity` inside a transaction. Test it with multiple threads.

**Stretch task:** add idempotency to orders and explain reservation expiry or payment rollback.

## 04 — Audit events with pagination

**Prompt:** Store events and support filtered page-based reads. Sort results newest first. Never return unlimited rows.

**What to think about:** SQL parameters, stable ordering, the cost of large OFFSETs, count queries, indexes.

**Implementation:** `audit_log_pagination.py` includes bounded pages, parameter binding, `event_type` filtering, and total counts.

**Stretch task:** replace OFFSET pagination with a cursor based on the event ID and explain what changes when new rows arrive between requests.

## 05 — Secure webhook receiver

**Prompt:** Accept a third-party callback only if its HMAC matches the raw request body and the timestamp is recent. Ignore duplicate event IDs.

**What to think about:** constant-time comparison, signature canonicalisation, clock skew, replay protection, secret rotation.

**Implementation:** `signed_webhook.py` checks the HMAC and tracks event IDs in memory. For real deployments, use an authenticated shared secret, durable replay storage, event schema validation, and a processing queue.

**Stretch task:** persist event IDs with a unique constraint and test replay prevention after application restart.

## 06 — Retry queue with dead-letter state

**Prompt:** Add background jobs to a durable store. A job can succeed, fail and retry, or reach a dead-letter state after too many failures.

**What to think about:** at-least-once delivery, backoff, idempotent consumers, worker crashes, poison messages, dead-letter queues.

**Implementation:** `retry_job_queue.py` is a small SQLite-backed training example. The `/worker/run-once` endpoint **must not be exposed in a real public service**; it represents a manually triggered demo worker.

**Stretch task:** add exponential backoff, durable job leases and an atomic claim to make multiple workers safe. In a full system, worker execution must not run as an unprotected API endpoint.

## How I would explain my code in an interview

For every round: explain the problem in one sentence; start with a simple solution; name the edge case that breaks the simple solution; show the implemented fix; run a test; discuss what is still missing for production.
