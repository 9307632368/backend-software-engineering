# Small task service — FastAPI starter

A simple task API that I can copy before building a bigger backend. The goal here is **clean request handling and tests**, not a production deployment.

## Features

- Health check: `GET /health`
- List tasks, with optional status filter: `GET /tasks?done=false`
- Create task: `POST /tasks`
- Read task: `GET /tasks/{task_id}`
- Mark task complete: `PATCH /tasks/{task_id}`
- Delete task: `DELETE /tasks/{task_id}`
- Request validation, 404 errors and isolated tests.

## Run on Windows

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m uvicorn app.main:app --reload
```

Check `http://127.0.0.1:8000/docs` for interactive requests.

## Design / limitations

The service stores data **in process memory**. Restarting the app clears data; multiple workers will not share state. For a real service I would add a database + migrations, persistent idempotency keys, auth and authorization, observability, and deployment checks. Dockerfile and CI files are starter examples only.

## 2024 package-era pins

The requirements choose versions available by 31 December 2024, rather than latest versions. They are provided for reproducible learning, not as a claim that they are currently security patched. If using them today, review advisories first.
