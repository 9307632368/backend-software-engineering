# 02 — File upload and download

**Track:** Backend Software Engineering / 2024 / Fundamentals / Practical Examples

## What I am practicing

Accept small files safely and let the client download or delete them.

2024-level concepts: multipart forms, stream reading, size limits, generated filenames, HTTP 413/415.

## Run it

Install the pinned requirements once from the **main repository root** with `python -m pip install -r requirements-dev.txt`. Then move into this folder and run:

```powershell
python -m uvicorn app:app --reload
```

Open <http://127.0.0.1:8000/docs>. `requests.http` has sample requests for VS Code REST Client.

## Try it yourself

Upload a .txt file, copy the returned ID, download it, and delete it. Try a .exe or a file larger than 1 MiB.

## How it can be improved

This only checks file extensions, not actual content. Real deployment needs antivirus scanning, authenticated access, quotas, content checks, durable metadata and object storage.

## Related files

- `app.py` — runnable service, with comments at the important steps.
- `requests.http` — test requests.
- `/tests/test_examples_02_*.py` — automated tests, located at the repository root.

**Note:** The year is a curriculum label. It does not mean the code was originally committed in 2024.
