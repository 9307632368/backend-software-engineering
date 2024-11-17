# Architecture notes and diagrams

The diagrams are written as Mermaid (`.mmd`) so I can track them in Git as text. GitHub also renders Mermaid in Markdown code fences.

1. `diagrams/01-request-flow.mmd` — simple layered service.
2. `diagrams/02-token-authorization.mmd` — token validation + ownership.
3. `diagrams/03-order-transaction.mmd` — transactional order flow.
4. `diagrams/04-background-jobs.mmd` — queue + retries + monitoring.

These are reference designs, **not claims that every component was deployed** in my projects.

## Why I separated layers

The endpoint should primarily validate HTTP input and map business exceptions to status codes. The service layer handles business rules; the repository handles database queries. This makes unit tests easier and lets us change one part without rewriting the whole API.

## What to document in a real design

- Main user request and expected response.
- Data storage and key tables.
- Trust boundaries and access control.
- Expected volume and what was actually measured.
- One failure mode and how we recover.
- What we explicitly did not build.
