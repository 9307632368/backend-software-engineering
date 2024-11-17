# API request examples

The files below target the **generated task API** from `templates/fastapi-starter/` and assume it is running locally on port 8000.

- `task-api.http`: requests for the VS Code REST Client extension.
- `powershell-requests.md`: equivalent commands without extensions.
- `create-task.json`: request body you can paste into the interactive Swagger docs.

Some requests depend on a task already existing, so start with POST first. The sample is in-memory; IDs reset when the server restarts.
