from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()

roles = {}
user_roles = {}


class RoleCreate(BaseModel):
    name: str


class PermissionCreate(BaseModel):
    permission: str


class UserRoleCreate(BaseModel):
    role: str


@app.post("/api/v1/roles")
def create_role(data: RoleCreate):
    if data.name not in roles:
        roles[data.name] = set()
    return {"role": data.name}


@app.post("/api/v1/roles/{role}/permissions")
def assign_permission(role: str, data: PermissionCreate):
    if role not in roles:
        roles[role] = set()
    roles[role].add(data.permission)
    return {"role": role, "permission": data.permission}


@app.post("/api/v1/users/{user}/roles")
def assign_role_to_user(user: str, data: UserRoleCreate):
    if user not in user_roles:
        user_roles[user] = set()
    user_roles[user].add(data.role)
    return {"user": user, "role": data.role}


@app.get("/api/v1/users/{user}/permissions/{permission}")
def check_permission(user: str, permission: str):
    allowed = False
    for role in user_roles.get(user, set()):
        if permission in roles.get(role, set()):
            allowed = True
            break
    return {"user": user, "permission": permission, "allowed": allowed}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)