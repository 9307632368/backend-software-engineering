# Flash sale incident review — simulated case

## Symptoms
- Stock becomes negative, or more orders are confirmed than inventory allows.
- A client retries after a network timeout and gets two orders.

## Root cause explored
The unsafe sequence is: `SELECT stock` → if enough → `UPDATE stock`. Two requests can pass the check before either update commits. Retry-handling is a separate problem: even perfect stock locking does not prevent duplicate requests when enough units exist.

## What changed in this implementation
1. `BEGIN IMMEDIATE` creates an explicit SQLite write transaction.
2. The decrement uses `UPDATE ... WHERE stock >= requested_quantity`.
3. A unique `(client_id, idempotency_key)` pair stores the original result.
4. Reusing a key with different order details produces `409 Conflict`.

## How I checked it
`test_parallel_buyers_do_not_oversell` starts 12 buyers competing for 5 units, then asserts that exactly 5 succeed and stock is zero. The test is repeatable; it is not a latency benchmark.

## Production follow-up
- Authenticate users instead of trusting client IDs.
- Load-test against a production database with connection pooling.
- Decide how long idempotency records should be retained.
- Add payments, inventory reservations, timeouts, and audit events.
