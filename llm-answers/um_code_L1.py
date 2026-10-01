from typing import Dict, List, Optional
from uuid import uuid4
import hashlib
import os

import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel


app = FastAPI()
PREFIX = "/api/v1"


class UserCreate(BaseModel):
    username: str
    password: str
    status: str = "active"
    role: Optional[str] = None
    permissions: List[str] = []


class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    status: Optional[str] = None
    role: Optional[str] = None
    permissions: Optional[List[str]] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class StatusUpdate(BaseModel):
    status: str


class RoleUpdate(BaseModel):
    role: Optional[str] = None


class PermissionsUpdate(BaseModel):
    permissions: List[str]


class PasswordReset(BaseModel):
    password: str


users: Dict[str, dict] = {}
tokens: Dict[str, str] = {}


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def public_user(user: dict) -> dict:
    return {
        "id": user["id"],
        "username": user["username"],
        "status": user["status"],
        "role": user["role"],
        "permissions": user["permissions"],
    }


admin_id = str(uuid4())
users[admin_id] = {
    "id": admin_id,
    "username": os.getenv("ADMIN_USERNAME", "admin"),
    "password": hash_password(os.getenv("ADMIN_PASSWORD", "admin")),
    "status": "active",
    "role": "admin",
    "permissions": [],
}


def current_user(authorization: Optional[str] = Header(default=None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    token = authorization[7:]
    user_id = tokens.get(token)
    user = users.get(user_id) if user_id else None

    if not user or user["status"] != "active":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return user


def admin_user(user: dict = Depends(current_user)) -> dict:
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return user


@app.post(f"{PREFIX}/auth/login")
def login(request: LoginRequest):
    for user in users.values():
        if (
            user["username"] == request.username
            and user["password"] == hash_password(request.password)
            and user["status"] == "active"
        ):
            token = str(uuid4())
            tokens[token] = user["id"]
            return {"access_token": token}

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@app.post(f"{PREFIX}/users")
def create_user(request: UserCreate, _: dict = Depends(admin_user)):
    user_id = str(uuid4())
    user = {
        "id": user_id,
        "username": request.username,
        "password": hash_password(request.password),
        "status": request.status,
        "role": request.role,
        "permissions": list(request.permissions),
    }
    users[user_id] = user
    return public_user(user)


@app.get(f"{PREFIX}/users")
def list_users(_: dict = Depends(admin_user)):
    return [public_user(user) for user in users.values()]


@app.get(f"{PREFIX}/users/{{user_id}}")
def get_user(user_id: str, _: dict = Depends(admin_user)):
    user = users.get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return public_user(user)


@app.put(f"{PREFIX}/users/{{user_id}}")
def update_user(user_id: str, request: UserUpdate, _: dict = Depends(admin_user)):
    user = users.get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    data = request.model_dump(exclude_unset=True)

    if "password" in data:
        data["password"] = hash_password(data["password"])

    user.update(data)
    return public_user(user)


@app.delete(f"{PREFIX}/users/{{user_id}}")
def delete_user(user_id: str, _: dict = Depends(admin_user)):
    if user_id not in users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    del users[user_id]

    for token, token_user_id in list(tokens.items()):
        if token_user_id == user_id:
            del tokens[token]

    return {"deleted": True}


@app.put(f"{PREFIX}/users/{{user_id}}/status")
def update_status(
    user_id: str,
    request: StatusUpdate,
    _: dict = Depends(admin_user),
):
    user = users.get(user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    user["status"] = request.status
    return public_user(user)


@app.put(f"{PREFIX}/users/{{user_id}}/role")
def assign_role(
    user_id: str,
    request: RoleUpdate,
    _: dict = Depends(admin_user),
):
    user = users.get(user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    user["role"] = request.role
    return public_user(user)


@app.put(f"{PREFIX}/users/{{user_id}}/permissions")
def update_permissions(
    user_id: str,
    request: PermissionsUpdate,
    _: dict = Depends(admin_user),
):
    user = users.get(user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    user["permissions"] = list(request.permissions)
    return public_user(user)


@app.post(f"{PREFIX}/users/{{user_id}}/password-reset")
def reset_password(
    user_id: str,
    request: PasswordReset,
    _: dict = Depends(admin_user),
):
    user = users.get(user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    user["password"] = hash_password(request.password)

    for token, token_user_id in list(tokens.items()):
        if token_user_id == user_id:
            del tokens[token]

    return {"reset": True}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8081)