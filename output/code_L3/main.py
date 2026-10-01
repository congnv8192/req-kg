from datetime import datetime, timezone
from enum import Enum
from math import ceil
from threading import Lock
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, Query, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, StrictStr, field_validator


API_PREFIX = "/api/v1"
VERSION = "1.0.0"


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def validate_iso8601(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None

    candidate = value
    if candidate.endswith("Z"):
        candidate = candidate[:-1] + "+00:00"

    try:
        datetime.fromisoformat(candidate)
    except ValueError:
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError("must be a valid ISO 8601 string") from exc

    return value


class CreateTaskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: StrictStr = Field(..., max_length=200)
    description: Optional[StrictStr] = Field(default=None, max_length=1000)
    priority: Priority
    due_date: Optional[StrictStr] = None

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, value: Optional[str]) -> Optional[str]:
        return validate_iso8601(value)


class UpdateTaskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[StrictStr] = Field(default=None, max_length=200)
    description: Optional[StrictStr] = Field(default=None, max_length=1000)
    priority: Optional[Priority] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[StrictStr] = None

    @field_validator("title", "priority", "status")
    @classmethod
    def reject_null_for_non_nullable_fields(cls, value: Any) -> Any:
        if value is None:
            raise ValueError("field may not be null")
        return value

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, value: Optional[str]) -> Optional[str]:
        return validate_iso8601(value)


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: Priority
    status: TaskStatus
    due_date: Optional[str]
    created_at: str
    updated_at: str


class PaginationResponse(BaseModel):
    page: int
    limit: int
    total: int
    pages: int


class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    pagination: PaginationResponse


app = FastAPI()

_tasks: Dict[int, Dict[str, Any]] = {}
_next_task_id = 1
_store_lock = Lock()


def error_response(
    code: int,
    message: str,
    details: Optional[Any] = None,
) -> JSONResponse:
    error: Dict[str, Any] = {
        "code": code,
        "message": message,
    }

    if details is not None:
        error["details"] = details

    return JSONResponse(
        status_code=code,
        content={"error": error},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    details = []

    for error in exc.errors():
        details.append(
            {
                "loc": list(error.get("loc", [])),
                "message": error.get("msg", "Validation error"),
                "type": error.get("type", "validation_error"),
            }
        )

    return error_response(
        422,
        "Validation failed",
        details,
    )


@app.exception_handler(Exception)
async def internal_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return error_response(
        500,
        "Internal server error",
    )


@app.post(
    f"{API_PREFIX}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(payload: CreateTaskRequest) -> Dict[str, Any]:
    global _next_task_id

    now = utc_now_iso()

    with _store_lock:
        task_id = _next_task_id
        _next_task_id += 1

        task = {
            "id": task_id,
            "title": payload.title,
            "description": payload.description,
            "priority": payload.priority.value,
            "status": TaskStatus.pending.value,
            "due_date": payload.due_date,
            "created_at": now,
            "updated_at": now,
        }

        _tasks[task_id] = task

    return task


@app.get(
    f"{API_PREFIX}/tasks",
    response_model=TaskListResponse,
)
async def list_tasks(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    status_filter: Optional[TaskStatus] = Query(default=None, alias="status"),
    priority: Optional[Priority] = Query(default=None),
) -> Dict[str, Any]:
    with _store_lock:
        tasks = list(_tasks.values())

    if status_filter is not None:
        tasks = [
            task
            for task in tasks
            if task["status"] == status_filter.value
        ]

    if priority is not None:
        tasks = [
            task
            for task in tasks
            if task["priority"] == priority.value
        ]

    total = len(tasks)
    pages = ceil(total / limit) if total > 0 else 0

    start = (page - 1) * limit
    end = start + limit

    return {
        "tasks": tasks[start:end],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": pages,
        },
    }


@app.get(
    f"{API_PREFIX}/tasks/{{task_id}}",
    response_model=TaskResponse,
)
async def get_task(task_id: int) -> Any:
    with _store_lock:
        task = _tasks.get(task_id)

    if task is None:
        return error_response(404, "Task not found")

    return task


@app.put(
    f"{API_PREFIX}/tasks/{{task_id}}",
    response_model=TaskResponse,
)
async def update_task(
    task_id: int,
    payload: UpdateTaskRequest,
) -> Any:
    updates = payload.model_dump(exclude_unset=True)

    if "priority" in updates:
        updates["priority"] = updates["priority"].value

    if "status" in updates:
        updates["status"] = updates["status"].value

    with _store_lock:
        task = _tasks.get(task_id)

        if task is None:
            return error_response(404, "Task not found")

        task.update(updates)
        task["updated_at"] = utc_now_iso()

        return dict(task)


@app.delete(
    f"{API_PREFIX}/tasks/{{task_id}}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_task(task_id: int) -> Response:
    with _store_lock:
        if task_id not in _tasks:
            return error_response(404, "Task not found")

        del _tasks[task_id]

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get(f"{API_PREFIX}/health")
async def health() -> Dict[str, str]:
    return {
        "status": "ok",
        "timestamp": utc_now_iso(),
        "version": VERSION,
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)