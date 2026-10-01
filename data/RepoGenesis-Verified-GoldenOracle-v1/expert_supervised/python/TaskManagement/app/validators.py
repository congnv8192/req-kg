"""
Manual, framework-agnostic validation for task payloads.

Validation is implemented by hand (rather than relying purely on a
framework's automatic model validation) so that we have full control over
the resulting HTTP status code and error envelope shape, which must match
exactly what the README specifies.
"""

import re
from datetime import datetime
from typing import Any, Dict, Optional

from app.config import settings
from app.errors import ValidationError

VALID_PRIORITIES = ("low", "medium", "high")
VALID_STATUSES = ("pending", "in_progress", "completed")

# Matches e.g. 2024-12-31T23:59:59Z / 2024-12-31T23:59:59.123Z /
# 2024-12-31T23:59:59+00:00 / 2024-12-31T23:59:59-05:00
_DATETIME_RE = re.compile(
    r"^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)
# Matches a bare date, e.g. 2024-12-31
_DATE_ONLY_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")


def validate_title(value: Any, *, required: bool) -> Optional[str]:
    if value is None:
        if required:
            raise ValidationError("title is required")
        return None
    if not isinstance(value, str):
        raise ValidationError("title must be a string")
    if value.strip() == "":
        raise ValidationError("title must not be empty or contain only whitespace")
    if len(value) > settings.TITLE_MAX_LENGTH:
        raise ValidationError(
            f"title must not exceed {settings.TITLE_MAX_LENGTH} characters"
        )
    return value


def validate_description(value: Any) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValidationError("description must be a string")
    if len(value) > settings.DESCRIPTION_MAX_LENGTH:
        raise ValidationError(
            f"description must not exceed {settings.DESCRIPTION_MAX_LENGTH} characters"
        )
    return value


def validate_priority(value: Any, *, required: bool) -> Optional[str]:
    if value is None:
        if required:
            raise ValidationError("priority is required")
        return None
    if not isinstance(value, str) or value not in VALID_PRIORITIES:
        raise ValidationError(f"priority must be one of {list(VALID_PRIORITIES)}")
    return value


def validate_status(value: Any) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str) or value not in VALID_STATUSES:
        raise ValidationError(f"status must be one of {list(VALID_STATUSES)}")
    return value


def validate_due_date(value: Any) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str) or value.strip() == "":
        raise ValidationError("due_date must be a non-empty ISO 8601 date string")

    match = _DATETIME_RE.match(value)
    if match:
        year, month, day, hour, minute, second = (int(g) for g in match.groups())
        try:
            datetime(year, month, day, hour, minute, second)
        except ValueError:
            raise ValidationError("due_date is not a valid calendar date/time")
        return value

    match = _DATE_ONLY_RE.match(value)
    if match:
        year, month, day = (int(g) for g in match.groups())
        try:
            datetime(year, month, day)
        except ValueError:
            raise ValidationError("due_date is not a valid calendar date")
        return value

    raise ValidationError("due_date must be in ISO 8601 format")


def validate_create_payload(payload: Any) -> Dict[str, Any]:
    """Validate the body of a POST /tasks request."""
    if not isinstance(payload, dict):
        raise ValidationError("Request body must be a JSON object")

    return {
        "title": validate_title(payload.get("title"), required=True),
        "description": validate_description(payload.get("description")),
        "priority": validate_priority(payload.get("priority"), required=True),
        "due_date": validate_due_date(payload.get("due_date")),
    }


def validate_update_payload(payload: Any) -> Dict[str, Any]:
    """Validate the body of a PUT /tasks/{id} request (partial update)."""
    if not isinstance(payload, dict):
        raise ValidationError("Request body must be a JSON object")

    result: Dict[str, Any] = {}
    if "title" in payload:
        result["title"] = validate_title(payload.get("title"), required=True)
    if "description" in payload:
        result["description"] = validate_description(payload.get("description"))
    if "priority" in payload:
        result["priority"] = validate_priority(payload.get("priority"), required=True)
    if "status" in payload:
        result["status"] = validate_status(payload.get("status"))
    if "due_date" in payload:
        result["due_date"] = validate_due_date(payload.get("due_date"))
    return result
