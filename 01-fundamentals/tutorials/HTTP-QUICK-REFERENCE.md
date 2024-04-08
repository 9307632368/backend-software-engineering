# HTTP quick reference

A browser, phone app or another backend sends an HTTP request to the API. The route is matched by **method + path**, query/path/body data is validated, the handler runs and returns a response.

```text
Client --> GET /books/2 --> FastAPI route --> validation --> handler --> JSON + status
                                                     |
                                                     +--> error response (e.g., 404)
```

| Method | Intended role | Tutorial example |
|---|---|---|
| GET | Read a resource or collection | `GET /tickets/1` |
| POST | Submit or create something | `POST /notes` |
| PATCH | Update selected fields | `PATCH /notes/1` |
| DELETE | Remove a resource | `DELETE /notes/1` |

## Three locations for input

- **Path:** `/tickets/42` — the ID identifies the resource.
- **Query:** `/tickets?limit=10` — controls which or how many results to return.
- **JSON body:** `{"subject":"Cannot log in","priority":"high"}` — structured data for creating a ticket.

## A request with PowerShell

`Invoke-RestMethod` converts a JSON response to a PowerShell object:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

For requests with a JSON body, set the method and content type:

```powershell
$body = @{ subject='Cannot log in'; priority='high' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/tickets -ContentType 'application/json' -Body $body
```

Run these commands **only while the relevant lesson app is serving on port 8000**. `/health` is provided by lesson 01; `/tickets` is provided by lesson 05.
