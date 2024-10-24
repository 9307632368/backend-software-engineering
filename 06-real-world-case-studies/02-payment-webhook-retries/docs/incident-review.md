# Payment webhook review — simulated incident

## Observed behavior in the fictional scenario
The same success message is processed repeatedly. A late failure message appears after success. In another example, an event arrives before a payment record exists.

## Failure modes
- Replaying events without a unique event ID can perform side effects twice.
- Trusting arbitrary JSON allows anyone to mark an order as paid.
- Changing a terminal state based only on arrival order can break downstream accounting.
- Dropping unknown payment IDs can lose a valid payment confirmation.

## Countermeasures implemented
- HMAC signature verification (constant-time signature comparison) and a five-minute time window.
- Unique `event_id` plus a stable fingerprint to detect altered retries.
- Pending-to-terminal state transitions; late contradictory status is ignored for this simplified demo.
- `awaiting_payment` events can be processed later using a reconciliation endpoint.

## How to test
Run `python -m pytest -q`. The tests cover duplicate events, invalid signatures, timestamp rejection, early delivery, contradictory late events, and wrong payment amounts.

## Follow-up for production
- Use the payment provider's real signing specification and verify HTTPS.
- Decide whether a state such as `failed` may be overturned by a later authoritative success event.
- Queue event processing, add dead-letter handling, and audit all reconciliations.
- Alert on discrepancies that require human review.
