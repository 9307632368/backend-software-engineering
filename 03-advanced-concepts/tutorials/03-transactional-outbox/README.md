# 03. Transactional outbox (orders + events)

Sometimes an API saves an order but crashes before sending its message. Then the business data and message broker disagree.

My small solution: save the order **and an outbox event in the same SQLite transaction**. A separate worker endpoint tries to publish pending events. If the fake broker fails, the event remains pending and can be retried.

Test it with `POST /orders`, `GET /events`, then `POST /worker/dispatch`. Run `python -m pytest -q tests`.

**Important:** This is a manual educational worker, not a reliable production dispatcher. A process may crash after publishing and before marking an event sent, so delivery is *at least once*. Consumers should deduplicate on event ID. For multiple workers, use row claiming/locks, backoff and dead-letter handling. No external broker is contacted.
