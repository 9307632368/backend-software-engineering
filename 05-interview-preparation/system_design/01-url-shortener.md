# System design round 01 — URL shortener

**Prompt (30 minutes):** Design a service that turns a long URL into a short code and redirects visitors to the original link.

## Clarify requirements before drawing boxes

- Should links expire? Can users edit them? Custom aliases?
- Is traffic mostly redirects or link creation?
- Do we need click analytics? Are redirects global?
- How should malicious or unsafe links be handled?

## Minimal working version

```text
Client --> POST /links --> API --> SQL database
Client --> GET /{code} --> API --> SQL database --> redirect
```

Suggested table: `links(id, code UNIQUE, original_url, created_at, expires_at, owner_id)`.

Endpoints: `POST /links` (validate URL, create code), `GET /{code}` (redirect / 404 / 410), `DELETE /links/{code}` (authorised owner only).

## Discuss the next bottlenecks

1. **Collisions:** random short codes need a UNIQUE constraint and retry strategy; database IDs can be encoded too, with tradeoffs for guessability.
2. **Latency:** the redirect is on the hot path. Cache `code -> URL`, with TTL and a cache invalidation strategy for updates/deletion.
3. **Abuse:** restrict URL schemes, rate limit creation, and add a URL safety policy.
4. **Metrics:** redirect requests/s, p95 latency, error rate, cache hit rate, link creation failures.
5. **Multi-region:** describe replication and whether a newly created code must be instantly visible everywhere.

## How I would explain it

Start with one API and a relational database, then scale based on the observed read/write ratio. Avoid starting with 15 services without a reason.

## Hands-on extension

Create a SQLite `links` table and implement `POST /links`, `GET /{code}` using the same `create_app()` pattern as the coding exercises. Add a test that two identical random codes cannot be inserted.
