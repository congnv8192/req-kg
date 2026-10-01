You are a requirements analyst. Extract ONLY the structured information the requirement EXPLICITLY STATES or DIRECTLY IMPLIES. Do NOT invent details. Output STRICTLY a single JSON object in the schema below — no prose, no fences.

========== REQUIREMENT (Level L3 — full SRS) ==========
# User Management Microservice
Functionality: RESTful user management — user CRUD, authentication, permission/role management, user status management, role assignment, password reset.

Service config: listening port 8081; base path /api/v1; content type application/json.

Endpoints:
1. POST /api/v1/users — create user. Input: username (required, min 3, max 50, alphanumeric, unique), email (required, valid email, unique), password (required, min 8), full_name (required, max 100), role (required, enum: user|admin|moderator), phone (optional, valid phone). Output: id, username, email, full_name, role, phone, status, created_at, updated_at.
2. GET /api/v1/users — list with pagination and filtering. Query: page (default 1), limit (default 10, max 100), status (enum: active|inactive|suspended), role (enum: user|admin|moderator), search (in username, email, full_name). Output: users[], pagination{page,limit,total,pages}.
3. GET /api/v1/users/{user_id} — retrieve one user.
4. PUT /api/v1/users/{user_id} — update (username, email, full_name, role, phone, status; all optional, same constraints).
5. DELETE /api/v1/users/{user_id} — delete user.
6. POST /api/v1/auth/login — authenticate. Input: username, password. Output: access_token, token_type, expires_in, user{id,username,email,role}.
7. POST /api/v1/users/{user_id}/reset-password — reset password. Input: new_password (required, min 8). Output: message.
8. GET /api/v1/health — health. Output: status, timestamp, version, database.

Error format: { error: { code, message, details } }. Codes: 400 bad request, 401 unauthorized, 403 insufficient permissions, 404 not found, 409 conflict (username/email exists), 422 validation failed, 500 internal error.

Data model — User: id (pk, auto int); username (required, 3-50, alphanumeric, unique); email (required, valid, unique); password_hash (required, encrypted); full_name (required, max 100); role (enum: user|admin|moderator); phone (optional, valid); status (enum: active|inactive|suspended, default active); created_at (auto); updated_at (auto).

Technical Specifications: strict input validation and type checking; complete error handling with user-friendly messages; complete operation logging including security events.

Deployment: must listen on port 8081; configuration (DB connection, JWT keys) via environment variables; provide health check endpoint; support Docker containerization; support database schema migration.
========== END REQUIREMENT ==========

Schema (include a key only if supported; use [] or null when nothing applies):
{
  "entities": ["<entity>"],
  "attributes": [{"name":"<field>","type":"<type|null>","required":<bool|null>,"max_length":<int|null>,"min_length":<int|null>,"enum":[<values>]|null,"default":"<value|null>","unique":<bool|null>}],
  "operations": [{"method":"<GET|POST|PUT|DELETE|null>","path":"<path|null>","action":"<create|list|retrieve|update|delete|login|reset_password|health|other>"}],
  "relations": [{"from":"<entity>","to":"<entity>","kind":"<relation>"}],
  "thresholds": [{"name":"<e.g. port, max_page_size, default_page_size, username_min_length, username_max_length, password_min_length, full_name_max_length, api_prefix>","value":<number|string>}],
  "nfr": [{"category":"<validation|error_handling|logging|health_check|deployment|configuration|containerization|auth|migration>","detail":"<short>"}]
}

Rules: capture every stated constraint (lengths, enum values, unique, port, limits) and every NFR (validation, logging, deployment/port, env config, health, Docker, migration, auth). Return ONLY the JSON.
