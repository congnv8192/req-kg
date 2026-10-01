"""
Application configuration.

All settings can be overridden via environment variables, as required by the
"Deployment Requirements" section of the README.
"""

import os


class Settings:
    """Central place for runtime configuration."""

    HOST: str = os.environ.get("HOST", "0.0.0.0")
    PORT: int = int(os.environ.get("PORT", "8080"))

    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Task Management Microservice"
    API_VERSION: str = os.environ.get("API_VERSION", "1.0.0")

    # SQLite connection string. Defaults to an in-memory database so every
    # fresh process run (and every test session) starts from a clean slate.
    # Set DATABASE_PATH to a file path (e.g. "/data/tasks.db") to persist
    # data across restarts.
    DATABASE_PATH: str = os.environ.get("DATABASE_PATH", ":memory:")

    DEFAULT_PAGE: int = 1
    DEFAULT_LIMIT: int = 10
    MAX_LIMIT: int = 100

    TITLE_MAX_LENGTH: int = 200
    DESCRIPTION_MAX_LENGTH: int = 1000


settings = Settings()
