# 07 — Pagination and Filtering: Product Catalog

Returning thousands of records in one response is slow and hard for clients to use. This example lets clients request a page of matching products.

## How to read the response

- `total`: the number of records **after filtering**, before pagination.
- `offset`: how many matching records to skip.
- `limit`: maximum number of records to return.
- `has_more`: whether another page exists.
- `items`: only the products for this page.

Try `GET /catalog?limit=2&offset=2`. You get the third and fourth items under the current sort order.

`sort_by` is restricted to `id`, `name`, and `price_paise`. That is useful practice for real database queries, where accepting untrusted column names can be dangerous. Sorting happens *before* slicing so results are consistent.

## Run

```powershell
python -m uvicorn app:app --reload
Invoke-RestMethod 'http://127.0.0.1:8000/catalog?category=accessories&sort_by=price_paise&order=desc'
```

## Exercises

1. Add a `max_price_paise` filter.
2. Return a `next_offset` value when `has_more` is true.
3. Research why offset pagination can behave strangely when new items are inserted between requests. How might cursor-based pagination help?

**Limit:** The six products are an in-memory example. A real catalog would filter and paginate in the database instead of reading every row first.
