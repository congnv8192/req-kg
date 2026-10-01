import os
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

import uvicorn
from fastapi import FastAPI, Header, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

PORT = int(os.getenv("PORT", "8082"))
HOST = os.getenv("HOST", "127.0.0.1")

favorites: List[Dict[str, Any]] = []
likes: List[Dict[str, Any]] = []
history: List[Dict[str, Any]] = []


class BodyModel(BaseModel):
    model_config = {"extra": "allow"}


def now():
    return datetime.now(timezone.utc).isoformat()


def require_token(authorization: Optional[str]):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    return authorization[7:]


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": str(exc.status_code),
                "message": exc.detail
            }
        },
    )


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "500",
                "message": "Internal server error"
            }
        },
    )


@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}


@app.post("/api/v1/favorites")
async def add_favorite(body: BodyModel, authorization: Optional[str] = Header(None)):
    user = require_token(authorization)
    record = dict(body.model_dump())
    record["favorite_id"] = str(uuid.uuid4())
    record["user_id"] = user
    record["created_at"] = now()
    favorites.append(record)
    return record


@app.get("/api/v1/favorites")
async def get_favorites(
    page: int = 1,
    limit: int = 10,
    content_type: Optional[str] = None,
    category: Optional[str] = None,
    authorization: Optional[str] = Header(None),
):
    user = require_token(authorization)

    items = [x for x in favorites if x["user_id"] == user]

    if content_type is not None:
        items = [x for x in items if x.get("content_type") == content_type]

    if category is not None:
        items = [x for x in items if x.get("category") == category]

    start = (page - 1) * limit

    return {
        "items": items[start:start + min(limit, 100)],
        "page": page,
        "limit": min(limit, 100),
    }


@app.delete("/api/v1/favorites/{favorite_id}")
async def delete_favorite(
    favorite_id: str,
    authorization: Optional[str] = Header(None),
):
    user = require_token(authorization)

    global favorites
    favorites = [
        x for x in favorites
        if not (x["favorite_id"] == favorite_id and x["user_id"] == user)
    ]

    return {"success": True}


@app.post("/api/v1/likes")
async def add_like(body: BodyModel, authorization: Optional[str] = Header(None)):
    user = require_token(authorization)

    record = dict(body.model_dump())
    record["like_id"] = str(uuid.uuid4())
    record["user_id"] = user
    record["created_at"] = now()

    likes.append(record)

    return record


@app.get("/api/v1/likes/stats/{content_id}")
async def get_like_stats(
    content_id: str,
    authorization: Optional[str] = Header(None),
):
    total = len([
        x for x in likes
        if x.get("content_id") == content_id
        and x.get("action") != "unlike"
    ])

    return {
        "content_id": content_id,
        "likes": total,
    }


@app.get("/api/v1/likes/history")
async def get_like_history(
    page: int = 1,
    limit: int = 10,
    content_type: Optional[str] = None,
    authorization: Optional[str] = Header(None),
):
    user = require_token(authorization)

    items = [
        x for x in likes
        if x["user_id"] == user
        and (
            content_type is None
            or x.get("content_type") == content_type
        )
    ]

    start = (page - 1) * limit

    return {
        "items": items[start:start + min(limit, 50)],
        "page": page,
        "limit": min(limit, 50),
    }


@app.post("/api/v1/history")
async def record_history(
    body: BodyModel,
    authorization: Optional[str] = Header(None),
):
    user = require_token(authorization)

    record = dict(body.model_dump())
    record["history_id"] = str(uuid.uuid4())
    record["user_id"] = user
    record["created_at"] = now()

    history.append(record)

    return record


@app.get("/api/v1/history")
async def get_history(
    page: int = 1,
    limit: int = 20,
    action: Optional[str] = None,
    content_type: Optional[str] = None,
    session_id: Optional[str] = None,
    authorization: Optional[str] = Header(None),
):
    user = require_token(authorization)

    items = [x for x in history if x["user_id"] == user]

    if action is not None:
        items = [x for x in items if x.get("action") == action]

    if content_type is not None:
        items = [x for x in items if x.get("content_type") == content_type]

    if session_id is not None:
        items = [x for x in items if x.get("session_id") == session_id]

    start = (page - 1) * limit

    return {
        "items": items[start:start + min(limit, 100)],
        "page": page,
        "limit": min(limit, 100),
    }


@app.delete("/api/v1/history/{history_id}")
async def delete_history(
    history_id: str,
    authorization: Optional[str] = Header(None),
):
    user = require_token(authorization)

    global history
    history = [
        x for x in history
        if not (x["history_id"] == history_id and x["user_id"] == user)
    ]

    return {"success": True}


@app.delete("/api/v1/history")
async def clear_history(
    authorization: Optional[str] = Header(None),
):
    user = require_token(authorization)

    global history
    history = [
        x for x in history
        if x["user_id"] != user
    ]

    return {"success": True}


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)