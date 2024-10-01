# Databases and SQL interview questions

### Q1. Why does `SELECT stock` followed by `UPDATE stock` fail under concurrency?
Two requests can both read `1`, each decide a sale is allowed, and then both write. Use an atomic conditional SQL update, locking, or another correct concurrency-control technique. See `concurrent_stock_orders.py`.

### Q2. What does ACID mean?
Atomicity (all-or-nothing transaction), Consistency (constraints preserved), Isolation (concurrent transactions interact according to the isolation level), and Durability (committed data survives according to the storage guarantees).

### Q3. What is a unique constraint used for?
It enforces uniqueness in the database even if the application receives overlapping requests. It is safer than `if not exists: insert` without a transaction or constraint.

### Q4. What is a database index? Why not index everything?
An index speeds selected lookups and ordering at the cost of storage and slower writes. Check query plans before adding too many indexes.

### Q5. What is SQL injection and how do you prevent it?
Attacker input modifies a query when code concatenates raw values into SQL. Use prepared statements / parameters. SQL values can be parameterised; dynamic SQL identifiers such as column names should use a strict allow-list.

### Q6. OFFSET vs keyset pagination?
OFFSET skips rows, which can become slow and can shift as rows are inserted. Keyset uses a stable cursor such as `(created_at, id)` and is more efficient for deep scrolling with correct ordering.

### Q7. What are the tradeoffs between SQL and NoSQL?
Start with access patterns and correctness needs. SQL is strong for related data and transactions. Document/key-value stores can be useful for specific scaling or data-shape requirements. Neither is universally best.

### Q8. What is the N+1 query problem?
Fetching a list then issuing one query per item creates many round trips. Use joins, eager loading or batch loading when appropriate.

### Practical follow-up
Make the stock-order test run with 10 simultaneous purchase attempts but only 2 stock units. Explain expected successes and failures.
