"""
Application factory.

Builds the FastAPI app, wires up routers, and installs exception handlers
that normalize *every* error response (including framework-level ones) into
the unified envelope required by the README:

    {"error": {"code": "...", "message": "...", "details": {...}}}
"""

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api import health, tasks
from app.config import settings
from app.errors import AppError


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.API_VERSION,
        description=(
            "RESTful API-based task management microservice providing "
            "CRUD operations, status tracking and priority management."
        ),
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url=f"{settings.API_V1_PREFIX}/docs",
        redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    )

    app.include_router(health.router, prefix=settings.API_V1_PREFIX, tags=["health"])
    app.include_router(tasks.router, prefix=settings.API_V1_PREFIX, tags=["tasks"])

    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError):
        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError):
        # Raised by FastAPI itself for things such as an invalid path/query
        # parameter type (e.g. a non-numeric task_id).
        body = {
            "error": {
                "code": "validation_error",
                "message": "Request validation failed",
                "details": jsonable_encoder(exc.errors()),
            }
        }
        return JSONResponse(status_code=422, content=body)

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(request: Request, exc: StarletteHTTPException):
        code = "not_found" if exc.status_code == 404 else "http_error"
        body = {"error": {"code": code, "message": str(exc.detail)}}
        return JSONResponse(status_code=exc.status_code, content=body)

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception):
        body = {
            "error": {
                "code": "internal_error",
                "message": "An unexpected error occurred",
            }
        }
        return JSONResponse(status_code=500, content=body)

    return app
