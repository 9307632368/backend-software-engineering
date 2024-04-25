# Tutorial 02 — Relationships to Transactions

I used a sample **wallet ledger** to understand why two related database updates should either both succeed or both fail. This is a learning demo, **not a banking/payment system**.

Run `python -m uvicorn app:app --reload` in this folder. Create two wallets, transfer some amount, then try to exceed the sender balance. A 409 response should leave both balances unchanged.

**Important limitation:** a read-then-update flow on SQLite alone is not a reliable concurrency strategy for real financial transfers. Use a DB-specific locking design, a proper ledger model, idempotency keys, and transaction isolation before building anything involving actual funds.

**Practice:** create a transfer-history table and test a database restart.
