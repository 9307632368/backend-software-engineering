# HTTP and REST quick notes

## HTTP verbs in a task API

| Verb | Endpoint example | Meaning | Typical status |
|---|---|---|---|
| GET | `/tasks` | Read list | 200 |
| GET | `/tasks/7` | Read one | 200, 404 |
| POST | `/tasks` | Create | 201, 422 |
| PUT | `/tasks/7` | Replace | 200/204, 404 |
| PATCH | `/tasks/7` | Update some fields | 200/204, 404 |
| DELETE | `/tasks/7` | Remove | 204, 404 |

`PUT` should be idempotent in effect. A plain `POST` is not necessarily idempotent. For payments or orders, an `Idempotency-Key` with persisted result can prevent duplicate business actions.

## Errors worth remembering

- `400` bad request (application chooses this for malformed business input).
- `401` unauthenticated, usually with proper challenge semantics.
- `403` authenticated but forbidden.
- `404` resource not found.
- `409` state conflict, e.g. duplicate unique username.
- `422` unprocessable entity / request validation failure (FastAPI's usual validation status).
- `429` too many requests, often with `Retry-After`.
- `500` unexpected server failure. Never include secrets or raw tracebacks in a public response.
- `503` unavailable temporarily; optionally `Retry-After`.

## Simple endpoint review

- Is the resource name plural and consistent?
- Is authentication required?
- Is input validated, including string length and value range?
- Is the status code meaningful?
- Is failure behavior documented?
- Does it have a test for a missing resource?
