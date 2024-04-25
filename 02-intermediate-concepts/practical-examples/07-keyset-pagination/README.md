# Practical 07 — Cursor Pagination

I wanted to understand the difference between offset pagination and **keyset pagination**. The API lists products by increasing database ID and uses the last seen ID as a cursor.

Create a few products, then request `GET /products?limit=2`. Use `next_cursor` as `after` on the next page. You can also filter by category or minimum price (paise).

This avoids large OFFSET scans for this simple ID-based ordering, but is not a complete general-purpose cursor API. Products inserted after pagination starts may appear in later pages, and deleting entries leaves gaps. Sorting by non-unique fields needs a compound key and cursor.

**Practice:** add `(created_at, id)` ordering and design an opaque signed cursor.
