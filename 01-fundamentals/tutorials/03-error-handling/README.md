# 03 — Error Handling: Stock Check

A successful HTTP response isn't enough. The API should also tell the client *why* a request can't be completed.

## Status codes in this lesson

| Status | Example | Meaning |
|---|---|---|
| 200 | Existing stock item | Request worked |
| 404 | SKU not in the catalog | Resource doesn't exist |
| 409 | Asked for more than is available | Request conflicts with current stock |
| 422 | Negative quantity | Request body fails validation |

`HTTPException` stops execution and generates an error response. The out-of-stock case uses 409 because it depends on current inventory, not malformed JSON.

## Run

```powershell
python -m uvicorn app:app --reload
Invoke-RestMethod http://127.0.0.1:8000/stock/keyboard
```

For error responses, Swagger `/docs` is easier to inspect than PowerShell's exception output. Sample HTTP calls are also in `requests.http`.

## Exercises

1. Create a route that returns **400** for an unsupported operation.
2. Return an error if the requested amount exceeds a per-order limit.
3. Explain why this app doesn't actually reserve inventory (it never mutates stock).

**Limit:** A real stock reservation must change storage atomically to prevent two concurrent customers claiming the same units. That is outside this lesson.
