# Design notes — Support Ticketing

```mermaid
flowchart LR
  Customer --> API[FastAPI]
  Agent --> API
  API --> Auth[JWT + role checks]
  API --> Tickets[Ticket service]
  Tickets --> DB[(SQLite relational DB)]
  Tickets --> Notes[Public and internal comments]
  Tickets --> Events[Audit trail]
```

Tables: `users`, `tickets`, `comments`, `ticket_events`. There are two permission layers: row visibility for ticket ownership and field visibility to hide internal comments. A ticket cannot jump directly from `open` to `resolved`; `closed` is terminal. Tests check those assumptions.

Tradeoff: this service is synchronous and SQLite-based to keep it simple. No actual SLA scheduler is implemented, and staff authentication/authorization would need external identity management for real deployment.
