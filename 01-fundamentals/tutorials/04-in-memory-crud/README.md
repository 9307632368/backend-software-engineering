# 04 — CRUD: Notes API

This is the first lesson where I implemented all four CRUD operations: Create, Read, Update and Delete.

## Endpoints

| Method | Route | Purpose |
|---|---|---|
| POST | `/notes` | Create a note; return **201** |
| GET | `/notes` | List all notes |
| GET | `/notes/{id}` | Read one note |
| PATCH | `/notes/{id}` | Change only selected fields |
| DELETE | `/notes/{id}` | Remove a note; return **204**, without a body |

For PATCH, `model_dump(exclude_unset=True)` means a missing `body` won't erase an existing note body. Passing an explicit `null` is rejected because the stored fields must be strings.

`create_app()` gives each test a fresh empty store and ID counter. Restarting the server also clears everything; the next lesson adds a database.

## Run

```powershell
python -m uvicorn app:app --reload
$body = @{ title='Backend practice'; body='Finish CRUD lesson' } | ConvertTo-Json
Invoke-RestMethod -Method Post http://127.0.0.1:8000/notes -ContentType application/json -Body $body
Invoke-RestMethod http://127.0.0.1:8000/notes
```

## Exercises

1. Add a `completed` Boolean field and a route to mark a note completed.
2. Try deleting the same note twice. Why is the second response **404**?
3. Restart Uvicorn and observe what happened to the stored notes.
