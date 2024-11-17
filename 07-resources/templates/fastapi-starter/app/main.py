from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field

app = FastAPI(title="Task Service", version="0.1.0")


class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    priority: int = Field(default=2, ge=1, le=3)


class TaskOut(TaskCreate):
    id: int
    done: bool = False


# This sample is intentionally in-memory. It does not support multiple workers.
_tasks: dict[int, TaskOut] = {}
_next_id = 1


def reset_data() -> None:
    """For isolated tests only. Never use as a public endpoint."""
    global _next_id
    _tasks.clear()
    _next_id = 1


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> TaskOut:
    global _next_id
    task = TaskOut(id=_next_id, title=payload.title, priority=payload.priority)
    _tasks[_next_id] = task
    _next_id += 1
    return task


@app.get("/tasks", response_model=list[TaskOut])
def list_tasks(done: bool | None = None) -> list[TaskOut]:
    records = [ _tasks[key] for key in sorted(_tasks) ]
    return [item for item in records if done is None or item.done == done]


@app.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int) -> TaskOut:
    task = _tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.patch("/tasks/{task_id}", response_model=TaskOut)
def complete_task(task_id: int) -> TaskOut:
    task = get_task(task_id)
    task.done = True
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int) -> Response:
    get_task(task_id)
    del _tasks[task_id]
    return Response(status_code=204)
