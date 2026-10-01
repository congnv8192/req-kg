"""Health check endpoint."""

from datetime import datetime, timezone

from fastapi import APIRouter

from app.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """GET /api/v1/health - report service health status."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
        "version": settings.API_VERSION,
    }
