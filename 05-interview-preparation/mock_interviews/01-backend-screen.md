# Mock interview 01 — 30-minute backend screening

This is a **practice script**, not a record of an interview I attended.

## Part A: Fundamentals (10 minutes)

1. Describe what happens from browser click to backend HTTP response.
2. When would you return 409 instead of 422?
3. Describe the difference between authentication and authorisation.
4. What is a transaction and why does a booking endpoint need one?
5. What does idempotency mean in the context of a POST endpoint?

## Part B: Debugging (10 minutes)

Scenario: Requests to `POST /orders` occasionally oversell an item. Error rate is low, but customers report negative stock.

Explain the bug using two request timelines. Name the database-level fix. Demonstrate the corresponding test in `tests/test_interview_apps.py`.

## Part C: Tradeoffs (10 minutes)

A project started with SQLite and one API process, but now has several replicas and significant write traffic. Explain what must change and what you would measure before migrating.

## Evaluation notes

Give yourself 0–2 for each: correctness, explanation clarity, identifying failure cases, proposed tests, and honesty about limitations. If you get stuck, write one thing to revise instead of memorising a long script.
