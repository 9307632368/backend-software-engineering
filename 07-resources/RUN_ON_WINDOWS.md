# Run and troubleshoot on Windows (PowerShell)

This section assumes **Python 3.11**, Windows PowerShell and Git.

## One-time checks

```powershell
py -3.11 --version
py -3.11 -m pip --version
git --version
```

## Test the resource tools

```powershell
py -3.11 -m unittest discover -s tests -v
```

## Generate a project from the starter

```powershell
py tools\scaffold_project.py --dest .\sample-backend
cd .\sample-backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m uvicorn app.main:app --reload
```

In another PowerShell window:

```powershell
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/health' -Method Get
$body = @{ title = 'Practice API testing'; priority = 2 } | ConvertTo-Json
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/tasks' -Method Post -ContentType 'application/json' -Body $body
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/tasks' -Method Get
```

## Common problems

- `py` not found: install Python 3.11 with the Windows launcher, or replace `py -3.11` with the correct `python` command.
- Scripts disabled: use `Set-ExecutionPolicy -Scope Process Bypass` **only if you understand your machine's policy**; alternatively call `.venv\Scripts\python.exe` without activating.
- Address already in use: `python -m uvicorn app.main:app --reload --port 8001`.
- `ModuleNotFoundError: app`: run the server and tests from **the generated project root**.
- `httpx` missing: install `requirements-dev.txt`; FastAPI's TestClient needs it.
- Cannot bind a port: check whether another application is listening on it.
- PowerShell `curl` behaves strangely: use `Invoke-RestMethod` or `curl.exe` rather than assuming `curl` is the Unix executable.

A local successful test run does not prove the service is ready for the public Internet.
