from fastapi import FastAPI, Header, HTTPException, Query, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import math
import uuid

app = FastAPI()

favorites = []
likes = []
history = []

CONTENT_TYPES = {"post", "article", "product", "video"}
LIKE_ACTIONS = {"like", "unlike"}
HISTORY_ACTIONS = {"view", "search", "share", "download"}


def now():
    return datetime.utcnow().isoformat()


def user_from_token(authorization: Optional[str], required=True):
    if required and (not authorization or not authorization.startswith("Bearer ")):
        raise HTTPException(
            status_code=401,
            detail={"error": "Unauthorized", "message": "Bearer Token required"}
        )
    return authorization.split(" ", 1)[1] if authorization else None


def error(message, status=400):
    raise HTTPException(
        status_code=status,
        detail={"error": "Bad Request", "message": message}
    )


def paginate(items, page, limit):
    total = len(items)
    start = (page - 1) * limit
    return {
        "items": items[start:start + limit],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": math.ceil(total / limit) if total else 0
        }
    }


class FavoriteCreate(BaseModel):
    content_id: str
    content_type: str
    category: Optional[str] = None


class LikeCreate(BaseModel):
    content_id: str
    content_type: str
    action: str


class HistoryCreate(BaseModel):
    action: str
    content_id: Optional[str] = None
    content_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None


@app.post("/api/v1/favorites")
def add_favorite(data: FavoriteCreate, authorization: Optional[str] = Header(None)):
    user_id = user_from_token(authorization)

    if data.content_type not in CONTENT_TYPES:
        error("Invalid content type")

    item = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "content_id": data.content_id,
        "content_type": data.content_type,
        "category": data.category,
        "created_at": now(),
        "updated_at": now()
    }

    favorites.append(item)
    return item


@app.get("/api/v1/favorites")
def get_favorites(
    authorization: Optional[str] = Header(None),
    page: int = 1,
    limit: int = 10,
    content_type: Optional[str] = None,
    category: Optional[str] = None
):
    user_id = user_from_token(authorization)

    items = [x for x in favorites if x["user_id"] == user_id]

    if content_type:
        items = [x for x in items if x["content_type"] == content_type]

    if category:
        items = [x for x in items if x["category"] == category]

    result = paginate(items, page, min(limit, 100))

    return {
        "favorites": [
            {
                **x,
                "content_info": {
                    "title": "",
                    "summary": "",
                    "thumbnail": ""
                }
            }
            for x in result["items"]
        ],
        "pagination": result["pagination"]
    }


@app.delete("/api/v1/favorites/{favorite_id}")
def delete_favorite(
    favorite_id: str,
    authorization: Optional[str] = Header(None)
):
    user_id = user_from_token(authorization)

    for i, item in enumerate(favorites):
        if item["id"] == favorite_id and item["user_id"] == user_id:
            favorites.pop(i)
            return {"message": "Favorite deleted"}

    raise HTTPException(
        status_code=404,
        detail={
            "error": "Not Found",
            "message": "Favorite not found"
        }
    )


@app.post("/api/v1/likes")
def add_like(data: LikeCreate, authorization: Optional[str] = Header(None)):
    user_id = user_from_token(authorization)

    if data.content_type not in CONTENT_TYPES:
        error("Invalid content type")

    if data.action not in LIKE_ACTIONS:
        error("Invalid action")

    item = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "content_id": data.content_id,
        "content_type": data.content_type,
        "action": data.action,
        "created_at": now(),
        "updated_at": now()
    }

    likes.append(item)

    return item


@app.get("/api/v1/likes/stats/{content_id}")
def like_stats(
    content_id: str,
    authorization: Optional[str] = Header(None)
):
    user_id = user_from_token(authorization, False)

    records = [
        x for x in likes
        if x["content_id"] == content_id
    ]

    return {
        "content_id": content_id,
        "content_type": records[-1]["content_type"] if records else "",
        "total_likes": len([
            x for x in records
            if x["action"] == "like"
        ]),
        "total_unlikes": len([
            x for x in records
            if x["action"] == "unlike"
        ]),
        "user_action": next(
            (
                x["action"]
                for x in reversed(records)
                if x["user_id"] == user_id
            ),
            None
        ) if user_id else None
    }


@app.get("/api/v1/likes/history")
def like_history(
    authorization: Optional[str] = Header(None),
    page: int = 1,
    limit: int = 10,
    content_type: Optional[str] = None
):
    user_id = user_from_token(authorization)

    items = [
        x for x in likes
        if x["user_id"] == user_id
    ]

    if content_type:
        items = [
            x for x in items
            if x["content_type"] == content_type
        ]

    result = paginate(items, page, min(limit, 50))

    return {
        "likes": [
            {
                k: x[k]
                for k in [
                    "id",
                    "content_id",
                    "content_type",
                    "action",
                    "created_at"
                ]
            }
            for x in result["items"]
        ],
        "pagination": result["pagination"]
    }


@app.post("/api/v1/history")
def record_history(
    data: HistoryCreate,
    request: Request,
    authorization: Optional[str] = Header(None)
):
    user_id = user_from_token(authorization)

    if data.action not in HISTORY_ACTIONS:
        error("Invalid action")

    item = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "action": data.action,
        "content_id": data.content_id,
        "content_type": data.content_type,
        "metadata": data.metadata or {},
        "session_id": data.session_id,
        "created_at": now(),
        "ip_address": request.client.host if request.client else "",
        "user_agent": request.headers.get("user-agent", "")
    }

    history.append(item)

    return item


@app.get("/api/v1/history")
def get_history(
    authorization: Optional[str] = Header(None),
    page: int = 1,
    limit: int = 20,
    action: Optional[str] = None,
    content_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    session_id: Optional[str] = None
):
    user_id = user_from_token(authorization)

    items = [
        x for x in history
        if x["user_id"] == user_id
    ]

    if action:
        items = [x for x in items if x["action"] == action]

    if content_type:
        items = [
            x for x in items
            if x["content_type"] == content_type
        ]

    if session_id:
        items = [
            x for x in items
            if x["session_id"] == session_id
        ]

    if start_date:
        items = [
            x for x in items
            if x["created_at"] >= start_date
        ]

    if end_date:
        items = [
            x for x in items
            if x["created_at"] <= end_date
        ]

    result = paginate(items, page, min(limit, 100))

    return {
        "history": [
            {
                **x,
                "content_info": {
                    "title": "",
                    "summary": ""
                }
            }
            for x in result["items"]
        ],
        "pagination": result["pagination"]
    }


@app.delete("/api/v1/history/{history_id}")
def delete_history(
    history_id: str,
    authorization: Optional[str] = Header(None)
):
    user_id = user_from_token(authorization)

    for i, item in enumerate(history):
        if item["id"] == history_id and item["user_id"] == user_id:
            history.pop(i)
            return {"message": "History deleted"}

    raise HTTPException(
        status_code=404,
        detail={
            "error": "Not Found",
            "message": "History not found"
        }
    )


@app.delete("/api/v1/history")
def clear_history(
    authorization: Optional[str] = Header(None)
):
    user_id = user_from_token(authorization)

    deleted = 0
    remaining = []

    for item in history:
        if item["user_id"] == user_id:
            deleted += 1
        else:
            remaining.append(item)

    history.clear()
    history.extend(remaining)

    return {
        "message": "History cleared",
        "deleted_count": deleted
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8082
    )