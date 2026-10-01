import os
import logging
from datetime import datetime, timedelta, timezone

import jwt
import uvicorn
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, EmailStr, Field


app = FastAPI()

logging.basicConfig(level=logging.INFO)

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "projectc-secret-key")
ALGORITHM = "HS256"
TOKEN_EXPIRE_SECONDS = 3600

users = {}
next_user_id = 1


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def error_response(message, error_code, details=None):
    response = {
        "success": False,
        "message": message,
        "error_code": error_code,
    }
    if details is not None:
        response["details"] = details
    return response


def create_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(seconds=TOKEN_EXPIRE_SECONDS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_authenticated_user(authorization):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail=error_response("Invalid authorization header", "AUTH_ERROR"),
        )

    token = authorization.split(" ", 1)[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        return users.get(user_id)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail=error_response("Invalid token", "AUTH_ERROR"),
        )


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=50)
    full_name: str = Field("", max_length=100)


class LoginRequest(BaseModel):
    username: str
    password: str


class UpdateUserRequest(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = Field(None, max_length=100)


@app.post("/api/v1/users/register")
def register(request: RegisterRequest):
    global next_user_id

    for user in users.values():
        if user["username"] == request.username:
            return error_response("Username already exists", "USER_EXISTS")

        if user["email"] == request.email:
            return error_response("Email already exists", "EMAIL_EXISTS")

    user = {
        "user_id": next_user_id,
        "username": request.username,
        "email": request.email,
        "password": request.password,
        "full_name": request.full_name,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }

    users[next_user_id] = user
    next_user_id += 1

    return {
        "success": True,
        "message": "User registered successfully",
        "data": {
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "created_at": user["created_at"],
        },
    }


@app.post("/api/v1/users/login")
def login(request: LoginRequest):
    user = None

    for item in users.values():
        if item["username"] == request.username:
            user = item
            break

    if not user or user["password"] != request.password:
        return error_response("Invalid username or password", "LOGIN_ERROR")

    token = create_token(user["user_id"])

    return {
        "success": True,
        "message": "Login successful",
        "data": {
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": TOKEN_EXPIRE_SECONDS,
            "user": {
                "user_id": user["user_id"],
                "username": user["username"],
                "email": user["email"],
                "full_name": user["full_name"],
            },
        },
    }


@app.get("/api/v1/users/{user_id}")
def get_user(user_id: int, authorization: str = Header(None)):
    get_authenticated_user(authorization)

    user = users.get(user_id)

    if not user:
        return error_response("User not found", "USER_NOT_FOUND")

    return {
        "success": True,
        "message": "User information retrieved successfully",
        "data": {
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "created_at": user["created_at"],
            "updated_at": user["updated_at"],
        },
    }


@app.put("/api/v1/users/{user_id}")
def update_user(
    user_id: int,
    request: UpdateUserRequest,
    authorization: str = Header(None),
):
    get_authenticated_user(authorization)

    user = users.get(user_id)

    if not user:
        return error_response("User not found", "USER_NOT_FOUND")

    if request.email is not None:
        user["email"] = request.email

    if request.full_name is not None:
        user["full_name"] = request.full_name

    user["updated_at"] = now_iso()

    return {
        "success": True,
        "message": "User updated successfully",
        "data": {
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "updated_at": user["updated_at"],
        },
    }


@app.delete("/api/v1/users/{user_id}")
def delete_user(user_id: int, authorization: str = Header(None)):
    get_authenticated_user(authorization)

    if user_id not in users:
        return error_response("User not found", "USER_NOT_FOUND")

    del users[user_id]

    return {
        "success": True,
        "message": "User deleted successfully",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8080,
    )
