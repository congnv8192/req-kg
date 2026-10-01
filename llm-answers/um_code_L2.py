from datetime import datetime, timezone
from hashlib import sha256
from typing import Optional
from uuid import uuid4

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel


app = FastAPI()

API_PREFIX = "/api/v1"
users: dict[str, dict] = {}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def hash_password(password: str) -> str:
    return sha256(password.encode("utf-8")).hexdigest()


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class ResetPasswordRequest(BaseModel):
    password: str


@app.post(f"{API_PREFIX}/users")
def create_user(payload: UserCreate):
    user_id = str(uuid4())
    timestamp = now_iso()

    user = {
        "id": user_id,
        "username": payload.username,
        "email": payload.email,
        "password_hash": hash_password(payload.password),
        "full_name": payload.full_name,
        "role": payload.role,
        "phone": payload.phone,
        "status": payload.status,
        "created_at": timestamp,
        "updated_at": timestamp,
    }

    users[user_id] = user
    return user


@app.get(f"{API_PREFIX}/users")
def list_users(
    page: int = Query(1),
    limit: int = Query(10),
    status: Optional[str] = None,
    role: Optional[str] = None,
    search: Optional[str] = None,
):
    result = list(users.values())

    if status is not None:
        result = [user for user in result if user["status"] == status]

    if role is not None:
        result = [user for user in result if user["role"] == role]

    if search is not None:
        search_lower = search.lower()
        result = [
            user
            for user in result
            if search_lower in user["username"].lower()
            or search_lower in user["email"].lower()
            or search_lower in (user["full_name"] or "").lower()
        ]

    start = (page - 1) * limit
    end = start + limit

    return result[start:end]


@app.get(f"{API_PREFIX}/users/{{id}}")
def get_user(id: str):
    user = users.get(id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@app.put(f"{API_PREFIX}/users/{{id}}")
def update_user(id: str, payload: UserUpdate):
    user = users.get(id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    updates = payload.model_dump(exclude_unset=True)

    if "password" in updates:
        user["password_hash"] = hash_password(updates.pop("password"))

    for key, value in updates.items():
        user[key] = value

    user["updated_at"] = now_iso()

    return user


@app.delete(f"{API_PREFIX}/users/{{id}}")
def delete_user(id: str):
    user = users.get(id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    del users[id]

    return user


@app.post(f"{API_PREFIX}/auth/login")
def login(payload: LoginRequest):
    password_hash = hash_password(payload.password)

    for user in users.values():
        if (
            user["username"] == payload.username
            and user["password_hash"] == password_hash
        ):
            return user

    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post(f"{API_PREFIX}/users/{{id}}/reset-password")
def reset_password(id: str, payload: ResetPasswordRequest):
    user = users.get(id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user["password_hash"] = hash_password(payload.password)
    user["updated_at"] = now_iso()

    return user


@app.get(f"{API_PREFIX}/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8081)