# Before implementing an API endpoint

- [ ] Resource and method make sense (`POST /orders` vs `GET /orders/{id}`).
- [ ] Request schema and constraints are clear.
- [ ] Response schema and status are documented.
- [ ] Caller identity and authorization are checked.
- [ ] DB write is transactional if multiple rows change.
- [ ] Duplicate / retried request behavior is defined.
- [ ] Pagination exists for potentially unbounded list endpoints.
- [ ] Validation, not-found and permission tests exist.
- [ ] Rate limits / timeouts are considered when relevant.
- [ ] Sensitive information is excluded from logs.
