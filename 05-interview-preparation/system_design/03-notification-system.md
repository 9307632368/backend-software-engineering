# System design round 03 — notification platform

**Prompt (35 minutes):** Send email, SMS, or in-app notifications without making the original request wait for the provider.

## Questions

- Does each event need every channel or one preferred channel?
- What happens if email fails temporarily?
- Can a user opt out?
- Are duplicate notifications acceptable?
- How long do we keep message history?

## Starting architecture

```text
Business API --> Event table + Outbox (one DB transaction)
                                  |
                                  v
                             Dispatcher
                                  |
                                  v
                         Durable job queue
                                  |
                      +-----------+-----------+
                      |           |           |
                   Email       SMS         In-app
                   worker      worker      worker
                      |
                      v
                  Provider API
```

Suggested data: `notification(id, user_id, template, channel, payload, status, attempts, next_retry_at)`.

The worker should acknowledge successful delivery correctly, retry temporary failures with backoff and jitter, and move poison messages to a dead-letter queue. Use provider delivery IDs when they exist. Redact private message content from operational logs.

## Important tradeoffs

- In-memory job queues are simple but lose work on restart.
- Database-backed queues can be fine at moderate throughput; dedicated brokers become useful for more complex routing and scale.
- At-least-once delivery means consumers should deduplicate.
- Retry only retryable errors; a permanently invalid email address should not be retried forever.
- Always enforce user preferences and notification consent.

## Hands-on extension

Take `retry_job_queue.py` and add `next_retry_at` with exponential backoff. Test that a failed job is **not** executed until its retry time. Explain how you would safely run two workers.
