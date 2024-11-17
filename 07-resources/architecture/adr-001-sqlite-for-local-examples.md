# ADR-001: Use SQLite in single-machine examples

- **Status:** Accepted for educational examples.
- **Context:** I want students to run an API without installing a separate DB server.
- **Decision:** SQLite for local single-machine examples; use PostgreSQL for exercises requiring stronger concurrency / multi-instance behavior.
- **Why:** SQLite is small, included with Python, and good for learning SQL and transactions.
- **Limitations:** Write contention, foreign keys need enabling, and its concurrency model differs from PostgreSQL. A passing SQLite test does not establish PostgreSQL behavior, nor production scalability.
- **Validation:** Local tests + transaction scenarios; use a separate PostgreSQL integration test before migrating a multi-user workload.
