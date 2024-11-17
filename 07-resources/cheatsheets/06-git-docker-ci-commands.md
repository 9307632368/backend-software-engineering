# Git, Docker and CI commands

## Git (PowerShell)

```powershell
git status
git switch -c feat/add-health-check
git add .
git commit -m "Add health endpoint and tests"
git log --oneline -5
git diff --stat
```

Before pushing: run tests; check `git status`; verify `.env`, databases, secrets, caches, and virtual environments are not tracked.

## Docker

```powershell
docker build -t sample-backend:local .
docker run --rm -p 8000:8000 sample-backend:local
docker ps
docker logs <container-id>
```

When deploying, do not publish sensitive containers with a shared demo password. Use environment variables/secret management and plan monitoring.

## GitHub Actions

Use `actions/checkout@v4` and `actions/setup-python@v5` for this 2024-era starter. In an actual production repository, pin action commits and update dependencies after security review; the 2024 sample deliberately reflects its time window.

## A practical CI checklist

- Run tests for every pull request.
- Fail if tests fail; don't swallow exit codes.
- Verify lockfiles or dependency pins are committed.
- Separate CI test credentials from production secrets.
- Use restricted workflow permissions, e.g. `contents: read` where possible.
