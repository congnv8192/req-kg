from fastapi import FastAPI, Depends, HTTPException, Query, Header
from pydantic import BaseModel
from typing import Optional
import uvicorn
from datetime import datetime
import uuid

app = FastAPI()

favorites = []
likes = []
history = []


def require_auth(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401)
    return authorization.split(" ", 1)[1]


class FavoriteCreate(BaseModel):
    content_id: str
    content_type: str
    category: Optional[str] = None


class LikeCreate(BaseModel):
    content_id: str
    content_type: str
    liked: bool


class HistoryCreate(BaseModel):
    content_id: str
    content_type: str
    action: str
    session_id: Optional[str] = None


@app.post("/api/v1/favorites")
def add_favorite(data: FavoriteCreate, token: str = Depends(require_auth)):
    item = {
        "favorite_id": str(uuid.uuid4()),
        "content_id": data.content_id,
        "content_type": data.content_type,
        "category": data.category,
        "created_at": datetime.utcnow().isoformat()
    }
    favorites.append(item)
    return item


@app.get("/api/v1/favorites")
def get_favorites(
    page: int = 1,
    limit: int = Query(10, le=100),
    content_type: Optional[str] = None,
    category: Optional[str] = None,
    token: str = Depends(require_auth)
):
    result = favorites

    if content_type:
        result = [x for x in result if x["content_type"] == content_type]

    if category:
        result = [x for x in result if x.get("category") == category]

    start = (page - 1) * limit
    return result[start:start + limit]


@app.delete("/api/v1/favorites/{favorite_id}")
def delete_favorite(favorite_id: str, token: str = Depends(require_auth)):
    global favorites
    favorites = [
        x for x in favorites
        if x["favorite_id"] != favorite_id
    ]
    return {"success": True}


@app.post("/api/v1/likes")
def add_like(data: LikeCreate, token: str = Depends(require_auth)):
    item = {
        "like_id": str(uuid.uuid4()),
        "content_id": data.content_id,
        "content_type": data.content_type,
        "liked": data.liked,
        "created_at": datetime.utcnow().isoformat()
    }
    likes.append(item)
    return item


@app.get("/api/v1/likes/stats/{content_id}")
def get_like_stats(content_id: str):
    liked = len([
        x for x in likes
        if x["content_id"] == content_id and x["liked"]
    ])

    unliked = len([
        x for x in likes
        if x["content_id"] == content_id and not x["liked"]
    ])

    return {
        "content_id": content_id,
        "likes": liked,
        "unlikes": unliked
    }


@app.get("/api/v1/likes/history")
def get_like_history(
    page: int = 1,
    limit: int = Query(10, le=50),
    content_type: Optional[str] = None,
    token: str = Depends(require_auth)
):
    result = likes

    if content_type:
        result = [
            x for x in result
            if x["content_type"] == content_type
        ]

    start = (page - 1) * limit
    return result[start:start + limit]


@app.post("/api/v1/history")
def record_history(data: HistoryCreate, token: str = Depends(require_auth)):
    item = {
        "history_id": str(uuid.uuid4()),
        "content_id": data.content_id,
        "content_type": data.content_type,
        "action": data.action,
        "session_id": data.session_id,
        "created_at": datetime.utcnow().isoformat()
    }

    history.append(item)
    return item


@app.get("/api/v1/history")
def get_history(
    page: int = 1,
    limit: int = Query(20, le=100),
    action: Optional[str] = None,
    content_type: Optional[str] = None,
    session_id: Optional[str] = None,
    token: str = Depends(require_auth)
):
    result = history

    if action:
        result = [
            x for x in result
            if x["action"] == action
        ]

    if content_type:
        result = [
            x for x in result
            if x["content_type"] == content_type
        ]

    if session_id:
        result = [
            x for x in result
            if x.get("session_id") == session_id
        ]

    start = (page - 1) * limit
    return result[start:start + limit]


@app.delete("/api/v1/history/{history_id}")
def delete_history(history_id: str, token: str = Depends(require_auth)):
    global history

    history = [
        x for x in history
        if x["history_id"] != history_id
    ]

    return {"success": True}


@app.delete("/api/v1/history")
def clear_history(token: str = Depends(require_auth)):
    global history
    history = []
    return {"success": True}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8082)
