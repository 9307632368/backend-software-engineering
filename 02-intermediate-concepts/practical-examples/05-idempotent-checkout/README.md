# Practical 05 — Idempotent Checkout (simulation)

Sometimes clients retry requests because they do not receive a response. I built this demo to understand why **the same request and idempotency key should not create a second checkout**.

Use `Idempotency-Key: cart-001` on `POST /checkouts`. Repeating the same payload returns the saved checkout; reusing that key with changed content gets HTTP 409.

This creates **demo checkout records only**. It does not charge cards, make bank transfers, reserve stock, or integrate with a payment provider. It deliberately uses SQLite and a simple single-key uniqueness rule. In a real service the key should be scoped to a merchant/customer, results should have an expiry policy, and providers may need reconciliation after partial failure.

Try two sequential requests with the same header; then change the quantity. Test the restart test as well.

**Practice:** add expiration for old keys, hide internal request fingerprints from returned responses, and record a request audit trail.
