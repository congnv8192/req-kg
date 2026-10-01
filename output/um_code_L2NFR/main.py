import os
import uuid
import hashlib
import hmac
import base64
import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any

import uvicorn
from fastapi import FastAPI, HTTPException, Query, Request
from pydantic import BaseModel

app = FastAPI(title="User Management Microservice", version="1.0.0")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("user-service")

DATABASE_URL = os.getenv("DATABASE_URL", "memory")
JWT_KEY = os.getenv("JWT_KEY", "development-key")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

users: Dict[int, Dict[str, Any]] = {}
next_id = 1


def now():
    return datetime.now(timezone.utc).isoformat()


def hash_password(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def create_token(user_id: int) -> str:
    payload = json.dumps({
        "user_id": user_id,
        "environment": ENVIRONMENT
    }).encode()

    signature = hmac.new(
        JWT_KEY.encode(),
        payload,
        hashlib.sha256
    ).digest()

    return base64.urlsafe_b64encode(
        payload + b"." + signature
    ).decode()


class UserCreate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password_hash: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password_hash: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None


class LoginRequest(BaseModel):
    username: Optional[str] = None
    password_hash: Optional[str] = None


class ResetPasswordRequest(BaseModel):
    password_hash: Optional[str] = None


@app.middleware("http")
async def request_logging(request: Request, call_next):
    logger.info(
        "request %s %s",
        request.method,
        request.url.path
    )

    response = await call_next(request)

    logger.info(
        "response %s %s",
        request.url.path,
        response.status_code
    )

    return response


@app.post("/api/v1/users")
def create_user(user: UserCreate):
    global next_id

    timestamp = now()

    data = (
        user.model_dump()
        if hasattr(user, "model_dump")
        else user.dict()
    )

    data.update({
        "id": next_id,
        "created_at": timestamp,
        "updated_at": timestamp
    })

    users[next_id] = data

    logger.info(
        "security event: user created id=%s",
        next_id
    )

    next_id += 1

    return data


@app.get("/api/v1/users")
def list_users(
    page: int = Query(1),
    limit: int = Query(10),
    status: Optional[str] = None,
    role: Optional[str] = None,
    search: Optional[str] = None,
):
    result = list(users.values())

    if status is not None:
        result = [
            u for u in result
            if u.get("status") == status
        ]

    if role is not None:
        result = [
            u for u in result
            if u.get("role") == role
        ]

    if search is not None:
        result = [
            u for u in result
            if (
                search.lower() in str(u.get("username", "")).lower()
                or search.lower() in str(u.get("email", "")).lower()
                or search.lower() in str(u.get("full_name", "")).lower()
            )
        ]

    start = (page - 1) * limit
    end = start + limit

    return result[start:end]


@app.get("/api/v1/users/{id}")
def get_user(id: int):
    user = users.get(id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user


@app.put("/api/v1/users/{id}")
def update_user(id: int, user: UserUpdate):
    existing = users.get(id)

    if existing is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    data = (
        user.model_dump(exclude_unset=True)
        if hasattr(user, "model_dump")
        else user.dict(exclude_unset=True)
    )

    existing.update(data)
    existing["updated_at"] = now()

    return existing


@app.delete("/api/v1/users/{id}")
def delete_user(id: int):
    if id not in users:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    del users[id]

    logger.info(
        "security event: user deleted id=%s",
        id
    )

    return {
        "detail": "User deleted"
    }


@app.post("/api/v1/auth/login")
def login(credentials: LoginRequest):
    for user in users.values():
        if (
            user.get("username") == credentials.username
            and user.get("password_hash") == credentials.password_hash
        ):
            logger.info(
                "security event: successful login user=%s",
                user["id"]
            )

            return {
                "access_token": create_token(user["id"]),
                "user": user
            }

    logger.info(
        "security event: failed login username=%s",
        credentials.username
    )

    raise HTTPException(
        status_code=401,
        detail="Invalid credentials"
    )


@app.post("/api/v1/users/{id}/reset-password")
def reset_password(
    id: int,
    request: ResetPasswordRequest
):
    user = users.get(id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user["password_hash"] = request.password_hash
    user["updated_at"] = now()

    logger.info(
        "security event: password reset user=%s",
        id
    )

    return user


@app.get("/api/v1/health")
def health():
    return {
        "status": "healthy",
        "environment": ENVIRONMENT,
        "database": DATABASE_URL
    }


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8081
    )