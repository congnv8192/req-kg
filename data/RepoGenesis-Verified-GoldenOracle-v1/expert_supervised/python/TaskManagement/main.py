"""
Entry point for the Task Management Microservice.

Run directly:
    python main.py

Or via uvicorn:
    uvicorn main:app --host 0.0.0.0 --port 8080
"""

from app.app_factory import create_app
from app.config import settings

app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
