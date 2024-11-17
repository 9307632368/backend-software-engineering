# Authentication and backend security

## Authentication is not authorization

- **Authentication:** who is calling? API key, session, JWT, OAuth2.
- **Authorization:** can this user access *this record*? Check ownership or permissions for every sensitive endpoint.

## Practical baseline

- Store passwords with a password-specific KDF such as bcrypt / Argon2, never plaintext or reversible encryption.
- Compare sensitive tokens in constant time where relevant (`hmac.compare_digest`).
- Do not put JWT signing secrets in source code or Git.
- Validate JWT algorithm, issuer/audience when used, and expiry. A JWT is not automatically encrypted.
- Use HTTPS in nonlocal deployments. CORS controls browser access, **not** API authentication.
- Limit upload size and validate server-side; don't trust an uploaded filename as a safe path.
- Rate-limit expensive or sensitive endpoints; do not rely only on frontend controls.
- Avoid logging passwords, bearer tokens, API keys, raw personal data.

## Example settings

```text
APP_ENV=development
JWT_SECRET=change-me-locally-never-commit-real-secrets
DATABASE_URL=sqlite:///./local.db
```

This is sample **documentation**, not a production secure configuration.

## 2024-style review exercise

For each endpoint in an example API, write: `public`, `user-only`, or `admin-only`. Then write a test showing that a non-owner cannot retrieve someone else's record even after logging in.
