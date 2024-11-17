# SQL transactions and persistence

## Common schema design

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE
);
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    status TEXT NOT NULL
);
CREATE INDEX idx_orders_user_id ON orders(user_id);
```

For SQLite, enable foreign-key enforcement per connection (for example `PRAGMA foreign_keys = ON`). PostgreSQL enforces foreign keys by default.

## Key rules

- Use parameterized SQL; never use user input to build raw SQL strings.
- Put related writes in a **single transaction**; either all commit or all roll back.
- Don't assume a `SELECT` followed by an `UPDATE` is safe when requests run concurrently.
- Add unique constraints for invariants such as a unique order idempotency key.
- Use migrations instead of manually editing a production schema.
- Verify query plans when an API becomes slow; indexes have write/storage costs too.

## Stock update idea (PostgreSQL)

```sql
UPDATE products
SET stock = stock - 1
WHERE id = :id AND stock > 0
RETURNING id, stock;
```

In a single transaction, this conditional write avoids the simple read-then-write race. If the update returns no row, the item is unavailable or absent. Investigate differences in database dialects and locking models before copying this to another DB.

## What I would test

Two clients attempting to buy the last item; a database exception midway through an order; duplicate requests; a restart between writes; stale reads; and a failing migration rollback.
