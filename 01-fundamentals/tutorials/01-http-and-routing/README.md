# 01 — HTTP and Routing: Book Finder

**What I practised:** the difference between a route, a request method, a path parameter and a query parameter.

## How it works

- `GET /health` returns a small status response so a client can see the app is responding.
- `GET /books` lists the books. Add `?category=systems` or `?search=deep` to filter results.
- `GET /books/2` reads a book by its ID. `GET /books/99` returns **404** because it doesn't exist.
- `POST /echo?message=hello` demonstrates a different HTTP method and the **201** status code. A real create route would usually accept a JSON body; that comes in lesson 02.

`book_id: int` makes FastAPI validate the path parameter. Try `/books/abc` and inspect the **422** response. The `X-Lesson` response header is an example of metadata sent to the client.

## Try it (PowerShell)

From this lesson's folder:

```powershell
python -m uvicorn app:app --reload
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod 'http://127.0.0.1:8000/books?category=systems'
```

The API documentation is at http://127.0.0.1:8000/docs. You can also use `requests.http`.

## Things to try

1. Add a fourth book and search for it by title.
2. Add a query parameter that matches a title exactly (case-insensitive).
3. Explain why `/books/99` is **404** and `/books/abc` is **422**.

**Limit:** Data lives in a constant dictionary, not a database. Don't use this as a real book management system.
