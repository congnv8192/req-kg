import uvicorn
from fastapi import FastAPI, HTTPException, Body
from typing import Any

app = FastAPI()

roles = {}
users = {}


@app.post("/api/v1/api/roles")
def create_role(data: dict[str, Any] = Body(...)):
    if not isinstance(data, dict) or "role_id" not in data or "name" not in data:
        raise HTTPException(status_code=400, detail="Invalid input")
    role_id = data["role_id"]
    name = data["name"]
    if not isinstance(role_id, str) or not isinstance(name, str):
        raise HTTPException(status_code=400, detail="Invalid input")
    roles[role_id] = {"name": name, "permissions": set()}
    return {"role_id": role_id, "name": name}


@app.post("/api/v1/api/roles/{role_id}/permissions")
def assign_permission_to_role(role_id: str, data: dict[str, Any] = Body(...)):
    if role_id not in roles:
        raise HTTPException(status_code=404, detail="Not found")
    if not isinstance(data, dict) or "permissions" not in data:
        raise HTTPException(status_code=400, detail="Invalid input")
    permissions = data["permissions"]
    if not isinstance(permissions, list) or not all(isinstance(p, str) for p in permissions):
        raise HTTPException(status_code=400, detail="Invalid input")
    roles[role_id]["permissions"].update(permissions)
    return {"role_id": role_id, "permissions": list(roles[role_id]["permissions"])}


@app.post("/api/v1/api/users/{user_id}/roles")
def assign_role_to_user(user_id: str, data: dict[str, Any] = Body(...)):
    if not isinstance(data, dict) or "roles" not in data:
        raise HTTPException(status_code=400, detail="Invalid input")
    assigned_roles = data["roles"]
    if not isinstance(assigned_roles, list) or not all(isinstance(r, str) for r in assigned_roles):
        raise HTTPException(status_code=400, detail="Invalid input")
    if any(r not in roles for r in assigned_roles):
        raise HTTPException(status_code=404, detail="Not found")
    if user_id not in users:
        users[user_id] = set()
    users[user_id].update(assigned_roles)
    return {"user_id": user_id, "roles": list(users[user_id])}


@app.get("/api/v1/api/users/{user_id}/permissions")
def get_user_permissions(user_id: str):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="Not found")
    permissions = set()
    for role_id in users[user_id]:
        if role_id in roles:
            permissions.update(roles[role_id]["permissions"])
    return {"user_id": user_id, "permissions": list(permissions)}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)