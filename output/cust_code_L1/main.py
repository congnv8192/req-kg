from fastapi import FastAPI, APIRouter, Body
from typing import Any
import uvicorn

app = FastAPI()

router = APIRouter(prefix="/api/v1")

favorites = set()
likes = set()
history = []

@router.post("/favorites")
def add_favorite(data: dict = Body(...)):
    favorites.add((data.get("user_id"), data.get("content_id")))
    return data

@router.get("/favorites/{user_id}")
def get_favorites(user_id: Any):
    return [
        {"user_id": item[0], "content_id": item[1]}
        for item in favorites
        if item[0] == user_id
    ]

@router.delete("/favorites")
def remove_favorite(data: dict = Body(...)):
    favorites.discard((data.get("user_id"), data.get("content_id")))
    return data

@router.post("/likes")
def add_like(data: dict = Body(...)):
    likes.add((data.get("user_id"), data.get("content_id")))
    return data

@router.get("/likes/{user_id}")
def get_likes(user_id: Any):
    return [
        {"user_id": item[0], "content_id": item[1]}
        for item in likes
        if item[0] == user_id
    ]

@router.delete("/likes")
def remove_like(data: dict = Body(...)):
    likes.discard((data.get("user_id"), data.get("content_id")))
    return data

@router.post("/history")
def add_history(data: dict = Body(...)):
    history.append(data)
    return data

@router.get("/history/{user_id}")
def get_history(user_id: Any):
    return [
        item
        for item in history
        if item.get("user_id") == user_id
    ]

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8082)
