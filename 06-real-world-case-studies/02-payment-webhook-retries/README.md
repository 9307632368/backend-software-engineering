# Case 02 — Duplicate and out-of-order payment webhooks

## Scenario (invented)

A payment provider delivers the same "paid" event more than once because the first HTTP response was lost. Sometimes the event reaches us before the local record has been created. Another event can arrive late, after the payment has already reached a terminal state.

## Implementation

- Signed `POST /webhooks/payment`, using timestamp-bound **HMAC-SHA256** verification of raw request bytes
- Duplicate delivery deduplication on `event_id` and exact payload fingerprint
- SQLite payment state machine: `pending` -> `succeeded` or `failed`
- Unmatched events retained for an explicit reconciliation step
- Protected internal endpoints for registering and inspecting **fake** payments

## Run

```powershell
python -m uvicorn payment_hooks.app:app --reload
```

Create a fake payment from another PowerShell window:

```powershell
$headers = @{'X-Internal-Api-Key'='local-demo-only-internal-key'}
$body = '{"payment_id":"pay_demo_001","amount_cents":1299}'
Invoke-RestMethod -Uri http://127.0.0.1:8000/internal/payments -Method Post -Headers $headers -ContentType application/json -Body $body
python tools/send_demo_webhook.py
Invoke-RestMethod -Uri http://127.0.0.1:8000/internal/payments/pay_demo_001 -Headers $headers
```

For early webhook deliveries, `POST /internal/reconcile` with the same internal key after the missing payment is registered.

## Lessons

I initially thought "return 200 on all webhooks" was enough. But that doesn't solve repeated updates, invalid signatures, or events arriving in a different order. The important parts were deduplicating events and making payment status changes deterministic.

## Limits

This case uses simulated payment records and **local demo secrets**. Do not connect it to a real payment processor. Production integrations must implement the provider's exact signature format, key rotation, retention policy, audit logs, safe reconciliation, and the vendor-specific transition rules. Local secrets must not be used on any public server. Read `docs/incident-review.md` and `docs/state-machine.md`.
