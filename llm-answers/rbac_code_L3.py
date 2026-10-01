
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import uuid

app = FastAPI()

roles = {}
users = {}


class RoleCreate(BaseModel):
    role_name: str


class PermissionAssign(BaseModel):
    permissions: list[str]


class RoleAssign(BaseModel):
    role_ids: list[str]


def error_response(message: str, status_code: int):
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "message": message
        }
    )


@app.post("/api/v1/api/roles")
async def create_role(data: RoleCreate):
    try:
        for role in roles.values():
            if role["role_name"] == data.role_name:
                return error_response("Role already exists", 400)

        role_id = str(uuid.uuid4())
        roles[role_id] = {
            "role_name": data.role_name,
            "permissions": []
        }

        return {
            "status": "success",
            "role_id": role_id,
            "role_name": data.role_name
        }
    except Exception:
        return error_response("Internal Server Error", 500)


@app.post("/api/v1/api/roles/{role_id}/permissions")
async def assign_permissions(role_id: str, data: PermissionAssign):
    try:
        if role_id not in roles:
            return error_response("Role not found", 404)

        for permission in data.permissions:
            if permission not in roles[role_id]["permissions"]:
                roles[role_id]["permissions"].append(permission)

        return {
            "status": "success",
            "role_id": role_id,
            "permissions": roles[role_id]["permissions"]
        }
    except Exception:
        return error_response("Internal Server Error", 500)


@app.post("/api/v1/api/users/{user_id}/roles")
async def assign_roles(user_id: str, data: RoleAssign):
    try:
        for role_id in data.role_ids:
            if role_id not in roles:
                return error_response("Role not found", 404)

        if user_id not in users:
            users[user_id] = []

        for role_id in data.role_ids:
            if role_id not in users[user_id]:
                users[user_id].append(role_id)

        return {
            "status": "success",
            "user_id": user_id,
            "role_ids": users[user_id]
        }
    except Exception:
        return error_response("Internal Server Error", 500)


@app.get("/api/v1/api/users/{user_id}/permissions")
async def get_user_permissions(user_id: str):
    try:
        if user_id not in users:
            return error_response("User not found", 404)

        permissions = set()
        for role_id in users[user_id]:
            if role_id in roles:
                permissions.update(roles[role_id]["permissions"])

        return {
            "status": "success",
            "user_id": user_id,
            "permissions": list(permissions)
        }
    except Exception:
        return error_response("Internal Server Error", 500)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
