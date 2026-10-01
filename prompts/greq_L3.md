You are a requirements analyst. Read the software requirement below and extract ONLY the structured information that the requirement EXPLICITLY STATES or DIRECTLY IMPLIES. Do NOT invent details that are not supported by the text. If something is not mentioned, leave it out.

Output STRICTLY as a single JSON object in the schema shown after the requirement. No prose, no markdown fences — just the JSON.

========== REQUIREMENT (Level L3 — full SRS) ==========
# Task Management Microservice

## Functionality Description
A RESTful API-based task management microservice providing complete task CRUD
operations and status management. Users can create, view, update and delete
tasks, with task status tracking and priority management.

## API Definition
Service configuration: listening port 8080; base path /api/v1; content type application/json.

Endpoints:
1. POST /api/v1/tasks — create task.
   Input: title (required, max 200 chars), description (optional, max 1000 chars),
   priority (required, enum: low|medium|high), due_date (optional, ISO 8601).
   Output: id, title, description, priority, status, due_date, created_at, updated_at.
2. GET /api/v1/tasks — list tasks with pagination and filtering.
   Query: page (default 1), limit (default 10, max 100),
   status (enum: pending|in_progress|completed), priority (enum: low|medium|high).
   Output: tasks[], pagination{page,limit,total,pages}.
3. GET /api/v1/tasks/{task_id} — retrieve one task.
4. PUT /api/v1/tasks/{task_id} — update a task (title, description, priority, status, due_date; all optional).
5. DELETE /api/v1/tasks/{task_id} — delete a task.
6. GET /api/v1/health — health check. Output: status, timestamp, version.

## Error Response Format
Unified error envelope: { error: { code, message, details } }.
Common codes: 400 (bad request), 404 (not found), 422 (validation failed), 500 (internal error).

## Data Model — Task
- id: primary key, auto-increment integer
- title: required, max 200 characters
- description: optional, max 1000 characters
- priority: enum [low, medium, high]
- status: enum [pending, in_progress, completed], default 'pending'
- due_date: optional, ISO 8601
- created_at: auto-generated
- updated_at: auto-updated

## Technical Specifications
- Framework: mainstream web framework (Flask, FastAPI, Django...).
- Database: relational (SQLite, PostgreSQL, MySQL...).
- Data validation: strict input data validation and type checking.
- Error handling: complete error handling and user-friendly error messages.
- Logging: complete operation logging.
- API documentation: auto-generated (Swagger/OpenAPI).

## Deployment Requirements
- Port: service must listen on port 8080.
- Environment variables: configure DB connection and other parameters via env vars.
- Health check: provide health check endpoint for monitoring.
- Containerization: support Docker containerized deployment.
========== END REQUIREMENT ==========

Output JSON schema (include a key only if the requirement supports it; use [] or null when nothing applies):
{
  "entities": ["<entity name>"],
  "attributes": [
    {"name":"<field>", "type":"<type or null>", "required":<true|false|null>,
     "max_length":<int or null>, "enum":[<values>] or null, "default":"<value or null>"}
  ],
  "operations": [
    {"method":"<GET|POST|PUT|DELETE or null>", "path":"<path or null>", "action":"<create|list|retrieve|update|delete|health|other>"}
  ],
  "relations": [{"from":"<entity>", "to":"<entity>", "kind":"<relation>"}],
  "thresholds": [{"name":"<e.g. port, max_page_size, default_page_size, title_max_length, description_max_length, api_prefix, api_version>", "value":<number or string>}],
  "nfr": [{"category":"<validation|error_handling|logging|health_check|deployment|configuration|api_docs|containerization>", "detail":"<short>"}]
}

Rules:
- Capture every constraint the text states (max_length, enum values, defaults, port, limits).
- Map "strict input validation" → nfr validation; "operation logging" → nfr logging; "Docker" → nfr containerization; "env vars" → nfr configuration; "health check endpoint" → nfr health_check + a health operation.
- Return ONLY the JSON object.
