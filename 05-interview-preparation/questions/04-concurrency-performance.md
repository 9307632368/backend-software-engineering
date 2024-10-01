# Concurrency, caching and performance

### Q1. Concurrency vs parallelism?
Concurrency means overlapping progress on tasks. Parallelism means tasks run at the same instant, often on multiple cores. Async I/O helps overlap waiting; it does not automatically speed up CPU-intensive computation.

### Q2. Race condition?
The outcome depends on interleaving of simultaneous operations. The last-stock problem is a classic example.

### Q3. What is optimistic vs pessimistic locking?
Optimistic concurrency checks that state/version has not changed before committing. Pessimistic locking holds a lock to block conflicting changes until work is finished. Each has different contention and failure tradeoffs.

### Q4. Why isn't a Python lock enough for a distributed API?
A lock protects threads in the same process, not different workers, containers, or machines. A shared transactional database or coordination mechanism is needed.

### Q5. Cache aside pattern?
Read cache first. On miss, load from database and populate cache. For updates, coordinate cache invalidation or versioning to avoid stale reads.

### Q6. Why use a queue for slow tasks?
It decouples the request from work such as sending email or processing files. It introduces worker reliability and delivery-semantics questions.

### Q7. At-most-once vs at-least-once job delivery?
At-most-once may lose failed work but avoids duplicate delivery. At-least-once retries failed work but needs idempotent consumers to tolerate duplicates. “Exactly once” usually requires careful constraints and end-to-end semantics.

### Q8. What metrics would you watch in an API?
Request volume, errors, latency percentiles (p50/p95/p99), saturation, database pool usage, and queue depth. A fast average can hide very slow outliers.

### Practical follow-up
In `sliding_window_rate_limit.py`, which data structure holds timestamps? Estimate the memory growth if 1 million API keys each make requests and then disappear.
