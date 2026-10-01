from datetime import datetime, timezone
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

tasks = {}
next_id = 1


class TaskCreate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[str] = None


def now():
    return datetime.now(timezone.utc).isoformat()


@app.post("/api/v1/tasks")
def create_task(task: TaskCreate):
    global next_id

    timestamp = now()
    created_task = {
        "id": next_id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "status": task.status,
        "due_date": task.due_date,
        "created_at": timestamp,
        "updated_at": timestamp,
    }

    tasks[next_id] = created_task
    next_id += 1

    return created_task


@app.get("/api/v1/tasks")
def list_tasks(
    page: int = 1,
    limit: int = 10,
    status: Optional[str] = None,
    priority: Optional[str] = None,
):
    result = list(tasks.values())

    if status is not None:
        result = [task for task in result if task["status"] == status]

    if priority is not None:
        result = [task for task in result if task["priority"] == priority]

    start = (page - 1) * limit
    end = start + limit

    return result[start:end]


@app.get("/api/v1/tasks/{id}")
def get_task(id: int):
    task = tasks.get(id)

    if task is None:
        raise HTTPException(status_code=404)

    return task


@app.put("/api/v1/tasks/{id}")
def update_task(id: int, update: TaskUpdate):
    task = tasks.get(id)

    if task is None:
        raise HTTPException(status_code=404)

    updates = update.model_dump(exclude_unset=True)

    for field, value in updates.items():
        task[field] = value

    task["updated_at"] = now()

    return task


@app.delete("/api/v1/tasks/{id}")
def delete_task(id: int):
    task = tasks.get(id)

    if task is None:
        raise HTTPException(status_code=404)

    return tasks.pop(id)


@app.get("/api/v1/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)