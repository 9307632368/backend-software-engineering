# 05 — SQLite Persistence: Support Tickets

The notes from lesson 04 disappeared every time I restarted the API. Here I added a local SQLite file, so tickets survive a restart.

## What happens behind the scenes

1. At startup, the app creates the `tickets` table if it doesn't exist.
2. Each request opens its own SQLite connection via `Depends(get_db)` and closes it afterwards.
3. `POST /tickets` inserts the data inside a transaction. The database generates the ticket ID.
4. `PATCH /tickets/{id}/close` changes the status, but a second close returns **409**.
5. The SQL statements use **? placeholders** rather than building a query by joining user input. This prevents SQL injection through normal field values.

The default database file is `data/support_tickets.db`, relative to the folder where Uvicorn is started. It is ignored by Git. Tests use a temporary database, so they won't overwrite local practice data.

## Run

```powershell
python -m uvicorn app:app --reload
$body = @{ subject='Unable to reset password'; priority='high' } | ConvertTo-Json
Invoke-RestMethod -Method Post http://127.0.0.1:8000/tickets -ContentType application/json -Body $body
Invoke-RestMethod http://127.0.0.1:8000/tickets
```

Restart the server, then retrieve `/tickets` again. The data should still be there.

## Exercises

1. Add a `/tickets?priority=high` filter using SQL parameters.
2. Add an `updated_at` timestamp column and document how you'd migrate an old database.
3. Explain why a server application may eventually need PostgreSQL, migrations, access control and connection pooling.

**Not production-ready:** this demo has no authentication, migrations or concurrency strategy for heavy write traffic.
