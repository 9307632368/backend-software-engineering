# Backend fundamentals — tutorials

I made these as small runnable lessons. Each one focuses on a different backend problem. I tried to keep the examples simple enough to understand but still show how the code behaves when something goes wrong.

| Order | Lesson | Working example | Main idea |
|---|---|---|---|
| 01 | [HTTP and routing](01-http-and-routing/README.md) | Book search API | Methods, URL parameters, response codes |
| 02 | [Request validation](02-request-validation/README.md) | Enrollment API | Pydantic, request bodies, 422 errors |
| 03 | [Error handling](03-error-handling/README.md) | Product stock API | 404, 409, business rules |
| 04 | [In-memory CRUD](04-in-memory-crud/README.md) | Notes API | POST/GET/PATCH/DELETE, state isolation |
| 05 | [SQLite persistence](05-sqlite-persistence/README.md) | Support tickets API | SQL, transactions, database lifecycle |
| 06 | [Dependencies and services](06-dependencies-and-services/README.md) | Shipping quote API | Separate business logic, dependency overrides |
| 07 | [Pagination and filters](07-pagination-and-filtering/README.md) | Product catalog API | Search, sorting, limit/offset |
| 08 | [API key permissions](08-api-key-permissions/README.md) | Protected notes API | Header authentication, read/write authorization |

## Setup (PowerShell)

Run from the `backend-software-engineering` root:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

**To run any lesson**, change into its directory and start Uvicorn:

```powershell
cd 01-fundamentals/tutorials/01-http-and-routing
python -m uvicorn app:app --reload --port 8000
```

Each app exposes `/docs` for interactive requests. All eight use port 8000 by default, so run only one at a time. Use `Ctrl+C` to stop.

Test individual lessons from the root, for example:

```powershell
python -m pytest tests/test_05_sqlite_persistence.py -q
```

**Tip:** `requests.http` can be opened in VS Code using the REST Client extension. No extension is needed if you prefer the Swagger UI at `/docs`.

## Learning checklist

- [ ] Explain the difference between a route, path parameter and query parameter.
- [ ] Send valid and invalid JSON; explain why validation errors happen.
- [ ] Explain when to use 200, 201, 204, 401, 403, 404, 409 and 422.
- [ ] Implement create/read/update/delete routes and write tests.
- [ ] Restart an API and check whether the stored data survives.
- [ ] Replace a service using `dependency_overrides` during a test.
- [ ] Add a sort and filter option without trusting arbitrary SQL input.
- [ ] Check that API keys are not committed or printed in logs.

## References

- [FastAPI tutorials](https://fastapi.tiangolo.com/tutorial/)
- [FastAPI testing with TestClient](https://fastapi.tiangolo.com/tutorial/testing/)
- [FastAPI dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [Pydantic validation](https://docs.pydantic.dev/latest/concepts/validators/)
- [Python sqlite3](https://docs.python.org/3/library/sqlite3.html)
- [HTTP status code reference (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status)

The code in these lessons was assembled specifically for this portfolio section; the references explain the patterns and APIs used. No third-party application is presented as original code.
