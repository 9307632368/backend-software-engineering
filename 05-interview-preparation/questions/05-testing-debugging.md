# Testing and debugging questions

### Q1. Unit vs integration vs end-to-end tests?
Unit tests isolate a small piece of logic. Integration tests check components together (e.g. API plus SQLite). End-to-end tests validate a user flow across the whole application. All three are useful in different proportions.

### Q2. Why should tests control time?
Real-time sleeps make tests slow and flaky. Inject a clock into a rate limiter or webhook handler so boundary times can be tested deterministically.

### Q3. How do you test retry behaviour?
Make a fake handler fail once and then succeed. Confirm the final state and exact attempt count. Also test permanent failure and dead-letter handling.

### Q4. How do you debug a sudden increase in HTTP 500 errors?
Check deploy history, error logs, recent dependency changes, request traces, database connectivity and resource saturation. Reproduce with a safe payload, roll back if necessary, and add a regression test.

### Q5. How would you investigate a slow endpoint?
Use latency metrics and tracing, inspect database query plans, review external calls and payload sizes, benchmark suspected bottlenecks, then measure after each change.

### Q6. What should never appear in logs?
Passwords, full access tokens, payment card data, private keys and unrelated personal data. Use structured fields with redaction instead.

### Q7. What is a flaky test?
A test whose result changes without a corresponding code change, often due to time, shared state, concurrency, ordering, or external services. Fix the root cause rather than only retrying it in CI.

### Q8. Why do tests use temporary databases?
They avoid polluting real data and minimise cross-test interference. The tests in this folder use independent SQLite files under pytest temporary paths.

### Practical follow-up
Break the stock constraint, run the tests, then fix the issue. Tell the interviewer which test prevented the bug from being merged.
