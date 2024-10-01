# System design round 02 — order or appointment booking service

**Prompt (40 minutes):** Design a booking API where two users must not reserve the same seat, room or appointment slot.

## Questions I would ask

- Is a booking confirmed immediately, or after payment?
- Can a booking expire while payment is pending?
- How many customers try the same slot at once?
- Can users cancel or reschedule?

## First design

```text
Web / Mobile
     |
     v
Booking API --> SQL database (unique slot + conditional state change)
     |
     +--> Outbox table --> Notification worker --> Email/SMS provider
```

Suggested tables:

- `slots(id, resource_id, starts_at, ends_at, capacity, reserved_count)`
- `bookings(id, user_id, slot_id, status, created_at)`
- `outbox(id, event_type, event_json, dispatched_at)`

A slot with capacity 1 can use a unique active booking constraint or a conditional update inside a transaction. For capacities greater than 1, decrement only when capacity remains. The code in `hands_on/concurrent_stock_orders.py` demonstrates the same underlying race.

## Typical failure cases

1. User taps twice: idempotency key should stop duplicate bookings.
2. Payment provider times out: model a pending state and reconcile later.
3. Email provider is down: booking should still persist; send notification asynchronously.
4. Two requests arrive simultaneously: use database correctness guarantees, not a local Python variable.
5. Client retries after 504: return the existing booking where possible.

## What to draw in the interview

Explain the request path, schema, reservation transaction, and reconciliation process. Discuss consistency before claiming the system can scale infinitely.

## Hands-on extension

Extend `concurrent_stock_orders.py` to support `PENDING`, `CONFIRMED`, `CANCELLED`, and a reservation deadline. Add a test for release of expired capacity.
