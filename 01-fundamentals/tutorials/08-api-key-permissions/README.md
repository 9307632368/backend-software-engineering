# 08 — API Key Permissions: Protected Memos

This final fundamentals tutorial checks who is calling the API and what they are allowed to do. I used two demo API keys: a reader key for `GET /memos`, and an admin key for both reading and creating memos.

## Setup (PowerShell)

You must set **both** secrets before starting the server:

```powershell
$env:DEMO_READ_KEY = 'change-this-reader-key-to-a-long-random-value'
$env:DEMO_ADMIN_KEY = 'change-this-admin-key-to-a-different-long-random-value'
python -m uvicorn app:app --reload
```

With `Invoke-RestMethod`, provide the key in the header:

```powershell
$headers = @{ 'X-API-Key' = $env:DEMO_READ_KEY }
Invoke-RestMethod http://127.0.0.1:8000/memos -Headers $headers
```

To create a memo, send a POST request with `$env:DEMO_ADMIN_KEY` instead. `/docs` also includes an **Authorize** control for the API-key header.

## Status codes

- **503** if both demo keys have not been configured.
- **401** if no key is sent or the key is wrong.
- **403** if a valid reader key tries to write.
- **201** when an admin key creates a memo.

The implementation uses `secrets.compare_digest()` to compare secrets and never includes secret values in responses.

## Exercises

1. Add a DELETE endpoint for admins only.
2. Add tests for missing, invalid, reader and admin keys.
3. Explain why browser-facing or public deployments need proper authentication, rate limiting, HTTPS, secret rotation, logging and audited access controls.

**Security note:** These are static demo keys stored in process configuration. Real systems generally require properly managed identities, expirations and authorization policies. The memos themselves are temporary and disappear on restart.
