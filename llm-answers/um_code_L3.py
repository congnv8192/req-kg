import os
import re
import json
import hmac
import base64
import hashlib
import logging
import secrets
import threading
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, Query, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, StrictStr, validator
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request


BASE_PATH = "/api/v1"
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
SECRET_KEY = os.getenv("SECRET_KEY", "development-secret-key-change-me")
TOKEN_EXPIRES_IN = int(os.getenv("TOKEN_EXPIRES_IN", "3600"))
PBKDF2_ITERATIONS = int(os.getenv("PASSWORD_PBKDF2_ITERATIONS", "260000"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8081"))

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("user-management-service")


class Role(str, Enum):
    user = "user"
    admin = "admin"
    moderator = "moderator"


class UserStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"


USERNAME_RE = re.compile(r"^[A-Za-z0-9]+$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_username(value: str) -> str:
    if len(value) < 3 or len(value) > 50:
        raise ValueError("username must be between 3 and 50 characters")
    if not USERNAME_RE.fullmatch(value):
        raise ValueError("username must contain only alphanumeric characters")
    return value


def validate_email(value: str) -> str:
    if not EMAIL_RE.fullmatch(value):
        raise ValueError("email must be a valid email address")
    return value


def validate_phone(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None

    if not value or value != value.strip():
        raise ValueError("phone must be a valid phone number")

    if not re.fullmatch(r"\+?[0-9][0-9()\-\s]{6,19}[0-9]", value):
        raise ValueError("phone must be a valid phone number")

    digits = re.sub(r"\D", "", value)
    if len(digits) < 8 or len(digits) > 15:
        raise ValueError("phone must be a valid phone number")

    return value


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)

    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )

    return "{}${}${}".format(
        PBKDF2_ITERATIONS,
        base64.urlsafe_b64encode(salt).decode("ascii"),
        base64.urlsafe_b64encode(derived).decode("ascii"),
    )


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        iterations_raw, salt_raw, expected_raw = stored_hash.split("$", 2)

        iterations = int(iterations_raw)
        salt = base64.urlsafe_b64decode(salt_raw.encode("ascii"))
        expected = base64.urlsafe_b64decode(expected_raw.encode("ascii"))

        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations,
        )

        return hmac.compare_digest(actual, expected)

    except (ValueError, TypeError):
        return False


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def create_access_token(user: Dict[str, Any]) -> str:
    now = int(utcnow().timestamp())

    header = {
        "alg": "HS256",
        "typ": "JWT",
    }

    payload = {
        "sub": str(user["id"]),
        "username": user["username"],
        "role": user["role"],
        "iat": now,
        "exp": now + TOKEN_EXPIRES_IN,
        "jti": secrets.token_hex(16),
    }

    encoded_header = b64url(
        json.dumps(
            header,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    )

    encoded_payload = b64url(
        json.dumps(
            payload,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    )

    signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")

    signature = hmac.new(
        SECRET_KEY.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()

    return f"{encoded_header}.{encoded_payload}.{b64url(signature)}"


class UserCreate(BaseModel):
    username: StrictStr
    email: StrictStr
    password: StrictStr
    full_name: StrictStr
    role: Role
    phone: Optional[StrictStr] = None

    @validator("username")
    def username_validator(cls, value: str) -> str:
        return validate_username(value)

    @validator("email")
    def email_validator(cls, value: str) -> str:
        return validate_email(value)

    @validator("password")
    def password_validator(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("password must be at least 8 characters")
        return value

    @validator("full_name")
    def full_name_validator(cls, value: str) -> str:
        if len(value) > 100:
            raise ValueError("full_name must not exceed 100 characters")
        return value

    @validator("phone")
    def phone_validator(cls, value: Optional[str]) -> Optional[str]:
        return validate_phone(value)


class UserUpdate(BaseModel):
    username: Optional[StrictStr] = None
    email: Optional[StrictStr] = None
    full_name: Optional[StrictStr] = None
    role: Optional[Role] = None
    phone: Optional[StrictStr] = None
    status: Optional[UserStatus] = None

    @validator("username")
    def username_validator(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return validate_username(value)

    @validator("email")
    def email_validator(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return validate_email(value)

    @validator("full_name")
    def full_name_validator(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value

        if len(value) > 100:
            raise ValueError("full_name must not exceed 100 characters")

        return value

    @validator("phone")
    def phone_validator(cls, value: Optional[str]) -> Optional[str]:
        return validate_phone(value)


class LoginRequest(BaseModel):
    username: StrictStr
    password: StrictStr


class ResetPasswordRequest(BaseModel):
    new_password: StrictStr

    @validator("new_password")
    def password_validator(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("new_password must be at least 8 characters")
        return value


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: Role
    phone: Optional[str]
    status: UserStatus
    created_at: datetime
    updated_at: datetime


class PaginationResponse(BaseModel):
    page: int
    limit: int
    total: int
    pages: int


class UserListResponse(BaseModel):
    users: List[UserResponse]
    pagination: PaginationResponse


class LoginUserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: Role


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: LoginUserResponse


class MessageResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    database: str


class ApiError(Exception):
    def __init__(
        self,
        status_code: int,
        message: str,
        details: Optional[Any] = None,
    ):
        self.status_code = status_code
        self.message = message
        self.details = details

        super().__init__(message)


def error_response(
    status_code: int,
    message: str,
    details: Optional[Any] = None,
) -> JSONResponse:
    error: Dict[str, Any] = {
        "code": status_code,
        "message": message,
    }

    if details is not None:
        error["details"] = details

    return JSONResponse(
        status_code=status_code,
        content={
            "error": error,
        },
    )


def public_user(user: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "full_name": user["full_name"],
        "role": user["role"],
        "phone": user["phone"],
        "status": user["status"],
        "created_at": user["created_at"],
        "updated_at": user["updated_at"],
    }


app = FastAPI(
    title="User Management Microservice",
    version=APP_VERSION,
)

_users: Dict[int, Dict[str, Any]] = {}
_next_user_id = 1
_storage_lock = threading.RLock()


@app.exception_handler(ApiError)
async def api_error_handler(
    _: Request,
    exc: ApiError,
) -> JSONResponse:
    return error_response(
        exc.status_code,
        exc.message,
        exc.details,
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    _: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    details = []

    for error in exc.errors():
        details.append(
            {
                "field": ".".join(
                    str(part)
                    for part in error.get("loc", [])
                ),
                "message": error.get(
                    "msg",
                    "Invalid value",
                ),
                "type": error.get(
                    "type",
                    "validation_error",
                ),
            }
        )

    return error_response(
        422,
        "Validation failed",
        details,
    )


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(
    _: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    if exc.status_code in {
        400,
        401,
        403,
        404,
        409,
        422,
    }:
        status_code = exc.status_code

    elif exc.status_code >= 500:
        status_code = 500

    else:
        status_code = 400

    default_messages = {
        400: "Bad request",
        401: "Unauthorized",
        403: "Insufficient permissions",
        404: "Not found",
        409: "Conflict",
        422: "Validation failed",
        500: "Internal server error",
    }

    message = (
        exc.detail
        if isinstance(exc.detail, str)
        else default_messages[status_code]
    )

    return error_response(
        status_code,
        message,
    )


@app.exception_handler(Exception)
async def internal_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.exception(
        "Unhandled internal error method=%s path=%s",
        request.method,
        request.url.path,
    )

    return error_response(
        500,
        "Internal server error",
    )


@app.post(
    f"{BASE_PATH}/users",
    response_model=UserResponse,
    status_code=201,
)
def create_user(
    payload: UserCreate,
) -> Dict[str, Any]:
    global _next_user_id

    with _storage_lock:
        for existing in _users.values():
            if existing["username"] == payload.username:
                logger.warning(
                    "Security event: duplicate username creation attempt "
                    "username=%s",
                    payload.username,
                )

                raise ApiError(
                    409,
                    "Username already exists",
                )

            if existing["email"] == payload.email:
                logger.warning(
                    "Security event: duplicate email creation attempt "
                    "email=%s",
                    payload.email,
                )

                raise ApiError(
                    409,
                    "Email already exists",
                )

        now = utcnow()

        user = {
            "id": _next_user_id,
            "username": payload.username,
            "email": payload.email,
            "password_hash": hash_password(payload.password),
            "full_name": payload.full_name,
            "role": payload.role.value,
            "phone": payload.phone,
            "status": UserStatus.active.value,
            "created_at": now,
            "updated_at": now,
        }

        _users[_next_user_id] = user
        _next_user_id += 1

    logger.info(
        "User created user_id=%s username=%s role=%s",
        user["id"],
        user["username"],
        user["role"],
    )

    return public_user(user)


@app.get(
    f"{BASE_PATH}/users",
    response_model=UserListResponse,
)
def list_users(
    page: int = Query(
        default=1,
        ge=1,
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
    status: Optional[UserStatus] = Query(
        default=None,
    ),
    role: Optional[Role] = Query(
        default=None,
    ),
    search: Optional[str] = Query(
        default=None,
    ),
) -> Dict[str, Any]:
    with _storage_lock:
        records = list(_users.values())

    if status is not None:
        records = [
            user
            for user in records
            if user["status"] == status.value
        ]

    if role is not None:
        records = [
            user
            for user in records
            if user["role"] == role.value
        ]

    if search is not None:
        needle = search.casefold()

        records = [
            user
            for user in records
            if needle in user["username"].casefold()
            or needle in user["email"].casefold()
            or needle in user["full_name"].casefold()
        ]

    records.sort(
        key=lambda user: user["id"]
    )

    total = len(records)

    pages = (
        (total + limit - 1) // limit
        if total
        else 0
    )

    start = (page - 1) * limit

    selected = records[
        start : start + limit
    ]

    logger.info(
        "Users listed page=%s limit=%s total=%s",
        page,
        limit,
        total,
    )

    return {
        "users": [
            public_user(user)
            for user in selected
        ],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": pages,
        },
    }


@app.get(
    f"{BASE_PATH}/users/{{user_id}}",
    response_model=UserResponse,
)
def get_user(
    user_id: int,
) -> Dict[str, Any]:
    with _storage_lock:
        user = _users.get(user_id)

    if user is None:
        raise ApiError(
            404,
            "User not found",
        )

    logger.info(
        "User retrieved user_id=%s",
        user_id,
    )

    return public_user(user)


@app.put(
    f"{BASE_PATH}/users/{{user_id}}",
    response_model=UserResponse,
)
def update_user(
    user_id: int,
    payload: UserUpdate,
) -> Dict[str, Any]:
    with _storage_lock:
        user = _users.get(user_id)

        if user is None:
            raise ApiError(
                404,
                "User not found",
            )

        updates = payload.dict(
            exclude_unset=True
        )

        if "username" in updates:
            if updates["username"] is None:
                raise ApiError(
                    422,
                    "Validation failed",
                    [
                        {
                            "field": "body.username",
                            "message": (
                                "none is not an allowed value"
                            ),
                        }
                    ],
                )

            for other_id, existing in _users.items():
                if (
                    other_id != user_id
                    and existing["username"]
                    == updates["username"]
                ):
                    logger.warning(
                        "Security event: duplicate username update "
                        "attempt user_id=%s username=%s",
                        user_id,
                        updates["username"],
                    )

                    raise ApiError(
                        409,
                        "Username already exists",
                    )

        if "email" in updates:
            if updates["email"] is None:
                raise ApiError(
                    422,
                    "Validation failed",
                    [
                        {
                            "field": "body.email",
                            "message": (
                                "none is not an allowed value"
                            ),
                        }
                    ],
                )

            for other_id, existing in _users.items():
                if (
                    other_id != user_id
                    and existing["email"]
                    == updates["email"]
                ):
                    logger.warning(
                        "Security event: duplicate email update "
                        "attempt user_id=%s email=%s",
                        user_id,
                        updates["email"],
                    )

                    raise ApiError(
                        409,
                        "Email already exists",
                    )

        for required_field in (
            "full_name",
            "role",
            "status",
        ):
            if (
                required_field in updates
                and updates[required_field] is None
            ):
                raise ApiError(
                    422,
                    "Validation failed",
                    [
                        {
                            "field": (
                                f"body.{required_field}"
                            ),
                            "message": (
                                "none is not an allowed value"
                            ),
                        }
                    ],
                )

        if "username" in updates:
            user["username"] = updates["username"]

        if "email" in updates:
            user["email"] = updates["email"]

        if "full_name" in updates:
            user["full_name"] = updates["full_name"]

        if "role" in updates:
            user["role"] = updates["role"].value

        if "phone" in updates:
            user["phone"] = updates["phone"]

        if "status" in updates:
            user["status"] = updates["status"].value

        user["updated_at"] = utcnow()

    logger.info(
        "User updated user_id=%s fields=%s",
        user_id,
        (
            ",".join(sorted(updates.keys()))
            if updates
            else "none"
        ),
    )

    if (
        "role" in updates
        or "status" in updates
    ):
        logger.info(
            "Security event: user authorization/status changed "
            "user_id=%s role=%s status=%s",
            user_id,
            user["role"],
            user["status"],
        )

    return public_user(user)


@app.delete(
    f"{BASE_PATH}/users/{{user_id}}",
    status_code=204,
)
def delete_user(
    user_id: int,
) -> Response:
    with _storage_lock:
        user = _users.get(user_id)

        if user is None:
            raise ApiError(
                404,
                "User not found",
            )

        del _users[user_id]

    logger.info(
        "Security event: user deleted "
        "user_id=%s username=%s",
        user_id,
        user["username"],
    )

    return Response(
        status_code=204
    )


@app.post(
    f"{BASE_PATH}/auth/login",
    response_model=LoginResponse,
)
def login(
    payload: LoginRequest,
) -> Dict[str, Any]:
    with _storage_lock:
        user = next(
            (
                candidate
                for candidate in _users.values()
                if candidate["username"]
                == payload.username
            ),
            None,
        )

    if (
        user is None
        or not verify_password(
            payload.password,
            user["password_hash"],
        )
    ):
        logger.warning(
            "Security event: failed login username=%s",
            payload.username,
        )

        raise ApiError(
            401,
            "Invalid username or password",
        )

    token = create_access_token(user)

    logger.info(
        "Security event: successful login "
        "user_id=%s username=%s",
        user["id"],
        user["username"],
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": TOKEN_EXPIRES_IN,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
        },
    }


@app.post(
    f"{BASE_PATH}/users/{{user_id}}/reset-password",
    response_model=MessageResponse,
)
def reset_password(
    user_id: int,
    payload: ResetPasswordRequest,
) -> Dict[str, str]:
    with _storage_lock:
        user = _users.get(user_id)

        if user is None:
            raise ApiError(
                404,
                "User not found",
            )

        user["password_hash"] = hash_password(
            payload.new_password
        )

        user["updated_at"] = utcnow()

    logger.info(
        "Security event: password reset "
        "user_id=%s username=%s",
        user_id,
        user["username"],
    )

    return {
        "message": "Password reset successfully"
    }


@app.get(
    f"{BASE_PATH}/health",
    response_model=HealthResponse,
)
def health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "timestamp": utcnow(),
        "version": APP_VERSION,
        "database": "in-memory",
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
    )