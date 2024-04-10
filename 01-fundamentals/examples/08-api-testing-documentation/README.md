# 08 — API testing and documentation

**Track:** Backend Software Engineering / 2024 / Fundamentals / Practical Examples

## What I am practicing

Build a book catalog and inspect the automatically generated OpenAPI specification.

2024-level concepts: response models, query validation, documented errors, TestClient, pytest.

## Run it

Install the pinned requirements once from the **main repository root** with `python -m pip install -r requirements-dev.txt`. Then move into this folder and run:

```powershell
python -m uvicorn app:app --reload
```

Open <http://127.0.0.1:8000/docs>. `requests.http` has sample requests for VS Code REST Client.

## Try it yourself

Add a book from /docs and inspect /openapi.json. Run the test suite and intentionally change an expectation to see a failure.

### Testing note
The tests check both correct responses and failure responses (for example 404 or 422). OpenAPI is automatically available at `/openapi.json`; a readable interface is available at `/docs`.

## How it can be improved

The example uses memory instead of a database and has no user authentication. API docs alone are not a substitute for a contract/versioning policy.

## Related files

- `app.py` — runnable service, with comments at the important steps.
- `requests.http` — test requests.
- `/tests/test_examples_08_*.py` — automated tests, located at the repository root.

**Note:** The year is a curriculum label. It does not mean the code was originally committed in 2024.
