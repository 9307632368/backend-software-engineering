# Mini Project 08 — Support Ticket API

I wanted a small application that is more realistic than one CRUD endpoint. This API creates support tickets, assigns them to an agent, follows a **state-transition rule**, and stores an event history.

## Main routes

- `POST /tickets` — customer creates a ticket
- `GET /tickets` and `GET /tickets/{id}` — browse tickets
- `PATCH /tickets/{id}/assign` — assign support agent
- `PATCH /tickets/{id}/status` — follow `open → in_progress → resolved → closed`
- `GET /tickets/{id}/history` — display audit entries

To run: `python -m uvicorn app:app --reload` and open `/docs`. To test agent-only operations in this **learning demonstration**, set request header `X-Actor-Role: agent`.

## What I learned

- Defining a lifecycle first is easier than allowing arbitrary status updates.
- Auditing a change in the same transaction helps keep the timeline consistent.
- A `409 Conflict` is more useful than silently accepting an impossible transition.

**Security warning:** `X-Actor-Role` is a **mock role selector**, not authentication. Anyone can forge it. Before real deployment, implement signed identity, enforce customer data isolation, validate emails properly, rate-limit endpoints, and use database migrations.

## Extend it

Add comments and attachments; search by assignee; prioritize tickets; add a valid authenticated `customer` role; and design a separate notification worker.
