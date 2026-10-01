"""
Custom application exceptions.

Every error raised from within the API layer is translated into the unified
error envelope documented in the README:

    {
        "error": {
            "code": "string",
            "message": "string",
            "details": "object (optional)"
        }
    }
"""

from typing import Any, Optional


class AppError(Exception):
    """Base class for all application-level errors that map to an HTTP response."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Optional[Any] = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)

    def to_dict(self) -> dict:
        error_body = {"code": self.code, "message": self.message}
        if self.details is not None:
            error_body["details"] = self.details
        return {"error": error_body}


class BadRequestError(AppError):
    """400 - malformed request (e.g. invalid JSON)."""

    def __init__(self, message: str = "Invalid request", details: Optional[Any] = None):
        super().__init__(400, "bad_request", message, details)


class ValidationError(AppError):
    """422 - request was well-formed but failed data validation."""

    def __init__(self, message: str = "Validation failed", details: Optional[Any] = None):
        super().__init__(422, "validation_error", message, details)


class NotFoundError(AppError):
    """404 - requested resource does not exist."""

    def __init__(self, message: str = "Resource not found", details: Optional[Any] = None):
        super().__init__(404, "not_found", message, details)


class InternalError(AppError):
    """500 - unexpected server error."""

    def __init__(self, message: str = "Internal server error", details: Optional[Any] = None):
        super().__init__(500, "internal_error", message, details)
