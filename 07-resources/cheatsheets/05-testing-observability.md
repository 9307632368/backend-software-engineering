# Testing and observing a backend

## Test types

| Type | What it checks | Example |
|---|---|---|
| Unit | Small business rule | Discount never goes negative |
| API / integration | Request validation and response | POST task returns 201 |
| Database integration | Query and commit | Rollback leaves no partial order |
| Contract | Request/response compatibility | OpenAPI contract and generated clients |
| Load | Performance under traffic | Latency at rising concurrent users |
| Security | Access control and malicious input | Users cannot fetch others' records |

## Useful logs

A good JSON log line records timestamp, level, action, request ID and a non-sensitive error code. It should not contain authorization tokens or unredacted user information.

## Useful metrics

- Total requests, error responses and in-flight requests.
- Latency percentiles (p50, p95, p99), with enough sample size.
- Database pool usage and slow query count.
- Queue depth, retry count, dead-letter count.

## Simple debugging sequence

1. Reproduce with a small request.
2. Read application logs and status codes.
3. Verify input, authentication and DB state.
4. Write a regression test.
5. Fix one thing and rerun the suite.
6. Document the limitation if there is one.

Do not publish fake charts as if they were measured in production.
