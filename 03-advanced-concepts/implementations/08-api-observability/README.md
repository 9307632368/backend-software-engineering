# 08. Request logs and API observability

A backend is harder to debug after deployment because requests happen at the same time. I added a middleware that creates an ID for every request, logs the route/status/duration as JSON and counts responses by method + route template + status.

Start the API, call `GET /work/12`, then visit `/metrics`. Check the terminal logs for the same `X-Request-ID` returned in the response. `/health/live` and `/health/ready` are basic health checks.

Run `python -m uvicorn app:app --reload` and `python -m pytest -q tests`.

**Limits:** In-memory metrics reset on restart, are separated by worker process and are not Prometheus-compatible. This demo also does not provide tracing or real dependency readiness probes. For production I would use OpenTelemetry, centralized logs, proper metrics and alerts. Do not log tokens, request bodies or personal data.
