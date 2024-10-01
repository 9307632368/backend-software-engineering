# Mock interview 02 — live coding (45 minutes)

Choose one task and avoid opening its solution until you have your own attempt.

## Task A — Retry-safe API (medium)

An endpoint receives `{customer_id, amount_paise}` and `Idempotency-Key`. Two requests with the same key and payload should create one record; a different payload with the same key should return a conflict.

**Acceptance criteria**

- Positive integer amount in paise.
- SQLite storage with a uniqueness guarantee.
- Return the same payment ID on a retry.
- Return 409 if key is reused for a different amount.
- Add one test for retries and one for conflicting payloads.

**Follow-up:** describe two concurrent retries and the behaviour after a service restart.

Compare with `hands_on/idempotent_payments.py`.

## Task B — Inventory race (medium/hard)

Stock for a SKU is 1. Five requests attempt to buy 1 at the same time. Exactly one order must be accepted.

**Acceptance criteria**

- No negative stock.
- Atomic deduction and order insertion.
- 409 on insufficient stock, 404 for unknown SKU.
- A concurrency test with five threads.

**Follow-up:** how does this change with PostgreSQL and multiple API servers?

Compare with `hands_on/concurrent_stock_orders.py`.

## Task C — API rate limit (medium)

Allow N requests per key in the last 60 seconds. Reject excess requests with 429 and an accurate `Retry-After` header.

**Acceptance criteria**

- A testable clock.
- Separate counters per key.
- Correct edge behaviour at exactly 60 seconds.
- Thread-safe updates.

**Follow-up:** explain how to enforce a shared limit across three service instances.

Compare with `hands_on/sliding_window_rate_limit.py`.

## Scoring

Give 0–2 points for each of: clear assumptions, correct implementation, edge cases, test quality, and ability to explain tradeoffs. 10 is a useful target; it is **not** an industry certification or benchmark.
