# PowerShell requests for the starter API

Run the app first (`python -m uvicorn app.main:app --reload`). From another PowerShell window:

```powershell
$base = 'http://127.0.0.1:8000'
Invoke-RestMethod -Method Get -Uri "$base/health"
$payload = @{ title = 'Test API manually'; priority = 2 } | ConvertTo-Json
$newTask = Invoke-RestMethod -Method Post -Uri "$base/tasks" -ContentType 'application/json' -Body $payload
$newTask
Invoke-RestMethod -Method Get -Uri "$base/tasks/$($newTask.id)"
Invoke-RestMethod -Method Patch -Uri "$base/tasks/$($newTask.id)"
Invoke-RestMethod -Method Delete -Uri "$base/tasks/$($newTask.id)"
```

Expected: POST creates a task, PATCH sets `done` to `true`, and DELETE responds with HTTP 204 and no body.
