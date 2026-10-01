You are a senior backend engineer. Implement the microservice described below as a SINGLE self-contained Python file.

Hard constraints:
- Framework: FastAPI. Expose the app as module-level `app`.
- Runnable with `uvicorn main:app --host 127.0.0.1 --port 8081`. Include `if __name__ == "__main__":` running uvicorn on 127.0.0.1:8081.
- Base path prefix /api/v1. In-memory storage. Output ONLY the Python code — no fences, no explanation.

Implement EXACTLY what the requirement states — all endpoints, all field constraints, all error behaviours, health, auth token, password reset. Do not add features not mentioned.

========== REQUIREMENT (Level L3 — full SRS) ==========
# User Management Microservice
Functionality: RESTful user management — user CRUD, authentication, permission/role management, user status management, role assignment, password reset.
Service config: port 8081; base path /api/v1; JSON.

Endpoints:
1. POST /api/v1/users — create user. Input: username (required, min 3, max 50, alphanumeric, unique), email (required, valid email, unique), password (required, min 8), full_name (required, max 100), role (required, enum: user|admin|moderator), phone (optional, valid phone). Output 201: id, username, email, full_name, role, phone, status, created_at, updated_at.
2. GET /api/v1/users — list with pagination and filtering. Query: page (default 1), limit (default 10, max 100), status (enum: active|inactive|suspended), role (enum: user|admin|moderator), search (username,email,full_name). Output: users[], pagination{page,limit,total,pages}.
3. GET /api/v1/users/{user_id} — retrieve one (404 if not found).
4. PUT /api/v1/users/{user_id} — update (username, email, full_name, role, phone, status; all optional, same constraints). 404 if not found.
5. DELETE /api/v1/users/{user_id} — delete (404 if not found).
6. POST /api/v1/auth/login — authenticate. Input: username, password. Output: access_token, token_type, expires_in, user{id,username,email,role}. 401 on bad credentials.
7. POST /api/v1/users/{user_id}/reset-password — reset. Input: new_password (required, min 8). Output: message.
8. GET /api/v1/health — Output: status, timestamp, version, database.

Error format: { "error": { "code": <int>, "message": <str>, "details": <optional> } }. Codes: 400 bad request, 401 unauthorized, 403 insufficient permissions, 404 not found, 409 conflict (username/email exists), 422 validation failed, 500 internal.

Data model — User: id (pk auto int); username (required, 3-50, alphanumeric, unique); email (required, valid, unique); password_hash (stores encrypted password); full_name (required, max 100); role (enum: user|admin|moderator); phone (optional, valid); status (enum: active|inactive|suspended, default active); created_at (auto); updated_at (auto).

Non-functional: strict input validation and type checking; complete error handling with the envelope above; operation logging including security events; listen on port 8081; config via environment variables; health check endpoint; Docker support.
========== END REQUIREMENT ==========

Output ONLY the Python code for main.py.
