# Security review for backend demos

## Inputs and data

- [ ] Validate types, lengths and bounds server-side.
- [ ] Parameterized SQL; no string concatenation of untrusted queries.
- [ ] Avoid user-controlled file paths, particularly for uploads.
- [ ] Reject oversized uploads and unexpected content types.

## Identity and access

- [ ] Passwords hashed with a modern KDF.
- [ ] Authentication and per-resource authorization are separate checks.
- [ ] Tokens have explicit expiry; secrets not committed.
- [ ] Authentication failures do not leak which users exist unless intentional.

## Operations

- [ ] Sensitive data excluded from logs and tracebacks.
- [ ] Dependencies reviewed for known issues before external deployment.
- [ ] Least-privilege database and CI permissions.
- [ ] CORS is not treated as access control.
- [ ] Retry and queue behavior cannot cause double business actions.
