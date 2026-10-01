"""Task CRUD endpoints."""

import json
import math
from typing import Optional

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from app import repository
from app.config import settings
from app.errors import BadRequestError, NotFoundError, ValidationError
from app.validators import (
    VALID_PRIORITIES,
    VALID_STATUSES,
    validate_create_payload,
    validate_update_payload,
)

router = APIRouter()


async def _read_json_body(request: Request) -> dict:
    """Read and parse the raw request body as JSON.

    Raises BadRequestError (-> HTTP 400) if the body is not valid JSON, which
    is distinct from a well-formed JSON body that fails schema validation
    (-> HTTP 422, raised by the validators module).
    """
    raw_body = await request.body()
    if not raw_body:
        return {}
    try:
        parsed = json.loads(raw_body)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise BadRequestError(
            "Request body is not valid JSON", details={"reason": str(exc)}
        )
    return parsed


def _task_not_found(task_id: int) -> NotFoundError:
    return NotFoundError(f"Task with id {task_id} not found")


@router.post("/tasks", status_code=201)
async def create_task(request: Request):
    """POST /api/v1/tasks - create a new task."""
    payload = await _read_json_body(request)
    data = validate_create_payload(payload)
    task = repository.create_task(data)
    return JSONResponse(status_code=201, content=task)


@router.get("/tasks")
async def get_tasks(
    page: int = Query(settings.DEFAULT_PAGE),
    limit: int = Query(settings.DEFAULT_LIMIT),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
):
    """GET /api/v1/tasks - list tasks with pagination and filtering."""
    if page < 1:
        raise ValidationError("page must be a positive integer")
    if limit < 1 or limit > settings.MAX_LIMIT:
        raise ValidationError(f"limit must be between 1 and {settings.MAX_LIMIT}")
    if status is not None and status not in VALID_STATUSES:
        raise ValidationError(f"status must be one of {list(VALID_STATUSES)}")
    if priority is not None and priority not in VALID_PRIORITIES:
        raise ValidationError(f"priority must be one of {list(VALID_PRIORITIES)}")

    tasks, total = repository.list_tasks(page, limit, status, priority)
    pages = math.ceil(total / limit) if total > 0 else 0

    return {
        "tasks": tasks,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": pages,
        },
    }


@router.get("/tasks/{task_id}")
async def get_task(task_id: int):
    """GET /api/v1/tasks/{task_id} - fetch a single task."""
    task = repository.get_task(task_id)
    if task is None:
        raise _task_not_found(task_id)
    return task


@router.put("/tasks/{task_id}")
async def update_task(task_id: int, request: Request):
    """PUT /api/v1/tasks/{task_id} - partially update a task."""
    payload = await _read_json_body(request)
    data = validate_update_payload(payload)
    task = repository.update_task(task_id, data)
    if task is None:
        raise _task_not_found(task_id)
    return task


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    """DELETE /api/v1/tasks/{task_id} - remove a task."""
    deleted = repository.delete_task(task_id)
    if not deleted:
        raise _task_not_found(task_id)
    return {"message": f"Task {task_id} deleted successfully"}
