import base64
import hashlib
import hmac
import json
import time
import uuid
from typing import Dict, Optional

import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel


app = FastAPI()
BASE_PATH = "/api/v1"
SECRET = "projectc-secret"

users: Dict[str, dict] = {}


class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


def b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def b64decode(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


def create_token(user_id: str) -> str:
    header = b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = b64encode(
        json.dumps({"sub": user_id, "exp": int(time.time()) + 3600}).encode()
    )
    message = f"{header}.{payload}".encode()
    signature = b64encode(hmac.new(SECRET.encode(), message, hashlib.sha256).digest())
    return f"{header}.{payload}.{signature}"


def verify_token(token: str) -> dict:
    try:
        header, payload, signature = token.split(".")
        message = f"{header}.{payload}".encode()
        expected = b64encode(
            hmac.new(SECRET.encode(), message, hashlib.sha256).digest()
        )

        if not hmac.compare_digest(signature, expected):
            raise ValueError()

        data = json.loads(b64decode(payload))

        if data["exp"] < int(time.time()):
            raise ValueError()

        return data
    except Exception:
        raise HTTPException(status_code=401)


def auth_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401)

    data = verify_token(authorization[7:])
    user = users.get(data["sub"])

    if not user:
        raise HTTPException(status_code=401)

    return user


@app.post(BASE_PATH + "/users")
def register(user: UserCreate):
    user_id = str(uuid.uuid4())

    users[user_id] = {
        "id": user_id,
        "username": user.username,
        "password": user.password,
        "email": user.email,
    }

    return users[user_id]


@app.post(BASE_PATH + "/login")
def login(request: LoginRequest):
    for user in users.values():
        if (
            user["username"] == request.username
            and user["password"] == request.password
        ):
            return {"token": create_token(user["id"])}

    raise HTTPException(status_code=401)


@app.get(BASE_PATH + "/users")
def list_users(_: dict = Depends(auth_user)):
    return list(users.values())


@app.get(BASE_PATH + "/users/{user_id}")
def get_user(user_id: str, _: dict = Depends(auth_user)):
    if user_id not in users:
        raise HTTPException(status_code=404)

    return users[user_id]


@app.put(BASE_PATH + "/users/{user_id}")
def update_user(
    user_id: str,
    update: UserUpdate,
    _: dict = Depends(auth_user),
):
    if user_id not in users:
        raise HTTPException(status_code=404)

    users[user_id].update(update.model_dump(exclude_unset=True))

    return users[user_id]


@app.delete(BASE_PATH + "/users/{user_id}")
def delete_user(user_id: str, _: dict = Depends(auth_user)):
    if user_id not in users:
        raise HTTPException(status_code=404)

    del users[user_id]

    return {"id": user_id}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
