# Design decisions and exercises

### Why a transaction and not a Python lock?
A `threading.Lock` would only protect requests in one Python process. A SQLite writer transaction works across database connections and processes sharing the same DB file. A production multi-node service should rely on an appropriate database or distributed coordination mechanism.

### Why integer cents?
`1.1 + 2.2` may not equal `3.3` exactly in binary floating-point arithmetic. Integer minor units are easier to reason about in an order total; currency and rounding requirements are outside this exercise.

### Exercises
1. Add a `cancel_order()` method that restores stock **exactly once**.
2. Add a reservation expiry time and a background cleanup task.
3. Write a test for 25 buyers and 10 units.
4. Replace SQLite with PostgreSQL and compare query/locking behavior.
