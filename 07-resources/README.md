# 07 - Backend resources (2024 collection)

This is my quick-reference folder for the **Backend Software Engineering** learning repository. I made it because I kept looking up the same things while writing APIs: status codes, database transactions, how to test an endpoint, and how to set up a new backend project.

These are **practical notes + small reusable tools**, not another copy of the full tutorials. The tools use only the Python standard library. A reusable FastAPI starter project is in `templates/fastapi-starter/`.

> **Year note:** This collection uses tooling and package releases available in or before December 2024. The `2024` label describes the portfolio curriculum, not the date a commit was made. Libraries are historical learning pins, not current security recommendations.

## What is here?

| Folder | Useful files |
|---|---|
| `roadmap/` | 2024 study route, repository map, practical learning log |
| `cheatsheets/` | HTTP, REST, FastAPI, SQL, auth, testing, Docker, Git, deployment |
| `architecture/` | Mermaid diagrams for a REST service, auth, transactions, workers |
| `templates/` | Working FastAPI starter, README, incident and ADR templates |
| `tools/` | Project scaffolder, API probe, section auditor (standard library) |
| `samples/` | PowerShell API requests, `.http` requests, JSON examples |
| `checklists/` | Pre-push checks, production-readiness and security review |
| `references/` | Links to original vendor documentation and selected release history |
| `tests/` | Tests for the small reusable tools |

## Quick start on Windows

From inside this `07-resources` folder:

```powershell
# The tools do not need third-party libraries
py -3.11 -m unittest discover -s tests -v

# Print missing top-level sections in the main GitHub repository
py tools\repo_audit.py --root ..

# Create a fresh mini API from the included template
py tools\scaffold_project.py --dest .\my-task-api
cd my-task-api
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` in your browser. Check `RUN_ON_WINDOWS.md` if the commands fail.

## A few things I learned

1. A working endpoint is not enough; I should test incorrect input too.
2. The HTTP method and status code are part of the API contract.
3. Do not hardcode database passwords or API keys, even for a sample project.
4. `SELECT` then `UPDATE` is not automatically safe under concurrency.
5. A postmortem should say what actually happened in a test scenario; it should not invent production metrics.

## Validation

- Run tool tests: `py -3.11 -m unittest discover -s tests -v`.
- Run the included FastAPI sample separately: `python -m pytest -q` from its root.
- The sample only stores tasks in memory; it is **not production persistence**. See `checklists/production-readiness.md` before extending it.

## License / sources

This folder contains original educational notes and scripts. Linked documentation belongs to its respective authors. See `references/official-links.md`. If you adapt someone else's source code later, keep its required license and attribution.
