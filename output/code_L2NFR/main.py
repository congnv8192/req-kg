from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
import os
import uuid
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("task-service")

DATABASE_CONFIG = os.getenv("DATABASE_URL", "")
SERVICE_PORT = int(os.getenv("PORT", "8080"))

app = FastAPI(title="Task Management Microservice")

router = APIRouter(prefix="/api/v1")

tasks: Dict[str, Dict[str, Any]] = {}


class TaskInput(BaseModel):
    model_config = ConfigDict(extra="allow")

    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskResponse(TaskInput):
    id: str
    created_at: datetime
    updated_at: datetime


def make_task(data: TaskInput) -> Dict[str, Any]:
    now = datetime.utcnow()
    return {
        "id": str(uuid.uuid4()),
        "title": data.title,
        "description": data.description,
        "priority": data.priority,
        "status": data.status,
        "due_date": data.due_date,
        "created_at": now,
        "updated_at": now,
    }


@router.post("/tasks", response_model=TaskResponse)
async def create_task(task: TaskInput):
    try:
        new_task = make_task(task)
        tasks[new_task["id"]] = new_task
        logger.info("Created task %s", new_task["id"])
        return new_task
    except Exception as exc:
        logger.error("Failed to create task: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to create task")


@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    page: Optional[int] = None,
    limit: Optional[int] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
):
    try:
        result = list(tasks.values())

        if status is not None:
            result = [task for task in result if task["status"] == status]

        if priority is not None:
            result = [task for task in result if task["priority"] == priority]

        if page is not None or limit is not None:
            current_page = page if page is not None else 1
            current_limit = limit if limit is not None else len(result)
            start = (current_page - 1) * current_limit
            result = result[start:start + current_limit]

        return result
    except Exception as exc:
        logger.error("Failed to list tasks: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to retrieve tasks")


@router.get("/tasks/{id}", response_model=TaskResponse)
async def get_task(id: str):
    try:
        task = tasks.get(id)

        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")

        return task
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to retrieve task %s: %s", id, exc)
        raise HTTPException(status_code=500, detail="Failed to retrieve task")


@router.put("/tasks/{id}", response_model=TaskResponse)
async def update_task(id: str, task_update: TaskInput):
    try:
        task = tasks.get(id)

        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")

        update_data = task_update.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            task[key] = value

        task["updated_at"] = datetime.utcnow()
        tasks[id] = task

        logger.info("Updated task %s", id)
        return task
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to update task %s: %s", id, exc)
        raise HTTPException(status_code=500, detail="Failed to update task")


@router.delete("/tasks/{id}")
async def delete_task(id: str):
    try:
        if id not in tasks:
            raise HTTPException(status_code=404, detail="Task not found")

        del tasks[id]

        logger.info("Deleted task %s", id)
        return {"message": "Task deleted"}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to delete task %s: %s", id, exc)
        raise HTTPException(status_code=500, detail="Failed to delete task")


@router.get("/health")
async def health():
    return {"status": "healthy"}


app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)