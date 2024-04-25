# Practical 06 — Verify Signed Webhooks

A webhook is a server-to-server HTTP callback. I simulated a provider and checked the body with an HMAC-SHA256 signature **before** parsing or storing the event. Duplicate event IDs are stored in SQLite.

```powershell
$env:WEBHOOK_SECRET = "local-test-secret"
python -m uvicorn app:app --reload
```

The `send_event.py` helper creates a signed request so you don't have to calculate hashes by hand.

```powershell
python send_event.py
```

**Security limits:** a real provider may have a different signature scheme. This example does not yet implement timestamp/replay windows, rate limits, payload schemas per event, or an async work queue. Do not reuse it unchanged as a production payment webhook endpoint.

**Practice:** add timestamp validation and a retry-capable outbox for event processing.
