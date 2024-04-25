# Tutorial 01 — Dependencies and Settings

**Goal:** avoid writing configuration checks inside every endpoint. I built a tiny quotation API with an environment-driven API key and a reusable FastAPI dependency.

## Try it

```powershell
$env:DEMO_API_KEY = "my-local-key"
python -m uvicorn app:app --reload
```

Visit `/docs` and call `POST /quotes`. Pass `x-api-key: my-local-key`. Prices use **paise (integer)**, so calculations do not introduce ordinary floating-point money errors. `get_settings` is overridden in tests; no real key is required.

**Practice:** add a configurable maximum quantity, return a friendlier error for an invalid tax configuration, and compare a dependency override against monkeypatching environment variables. Do not commit an actual key.
