# 05. Multi-tenant reporting — system design + API

**Scenario:** two companies use one reporting service. A query without a tenant filter can leak Company A's orders to Company B.

The example maps a **demo API key to a tenant on the server**. Every SQL read and write is scoped using that tenant. I also test that adding an arbitrary `X-Tenant-Id` header cannot change which tenant is selected. Money stays in integer cents to avoid rounding mistakes.

Run `python -m uvicorn app:app --reload`, `python -m pytest -q tests` and read `DESIGN.md` for the stronger approach I would use in production.

**Security note:** `demo-red-key` and `demo-blue-key` are deliberately public training credentials, not secrets. Real deployments need verified OIDC/JWT identities, secret management, key rotation, audit logging and database-level policies such as PostgreSQL RLS.
