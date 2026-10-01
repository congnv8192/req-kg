You are a senior backend engineer. Implement the microservice described by the requirement below as a SINGLE self-contained Python file.

Hard constraints (must follow exactly):
- Framework: FastAPI. Expose the app as a module-level variable named `app`.
- The file must be runnable with: `uvicorn main:app --host 127.0.0.1 --port 8080`.
- Also include an `if __name__ == "__main__":` block that runs uvicorn on host 127.0.0.1 port 8080.
- Base path prefix: /api/v1 for all endpoints.
- Storage: in-memory (a dict is fine); no external database.
- Output ONLY the Python source code — no markdown fences, no explanation. Start with the imports.

Implement EXACTLY what the requirement states — all endpoints, all field constraints, all error behaviours, the health endpoint. Do not add features the requirement does not mention.

========== REQUIREMENT (Level L3 — full SRS) ==========
# Task Management Microservice

## Functionality
A RESTful task management microservice: create, view, update, delete tasks, with status tracking and priority management.

## API (base path /api/v1, port 8080, JSON)
1. POST /api/v1/tasks — create task.
   Input: title (required, max 200 chars), description (optional, max 1000 chars),
   priority (required, one of: low|medium|high), due_date (optional, ISO 8601).
   On success return 201 with: id, title, description, priority, status, due_date, created_at, updated_at.
2. GET /api/v1/tasks — list tasks with pagination and filtering.
   Query: page (default 1), limit (default 10, max 100),
   status (one of: pending|in_progress|completed), priority (one of: low|medium|high).
   Return 200 with: { tasks: [...], pagination: {page, limit, total, pages} }.
3. GET /api/v1/tasks/{task_id} — retrieve one task (404 if not found).
4. PUT /api/v1/tasks/{task_id} — update a task (title, description, priority, status, due_date; all optional). 404 if not found.
5. DELETE /api/v1/tasks/{task_id} — delete a task (404 if not found).
6. GET /api/v1/health — return { status, timestamp, version }.

## Error format
On error return the envelope: { "error": { "code": <int>, "message": <str>, "details": <optional> } }.
Use 400 for bad request, 404 for not found, 422 for validation failure, 500 for internal error.

## Data model — Task
- id: auto-increment integer, primary key
- title: string, required, max 200
- description: string, optional, max 1000
- priority: one of [low, medium, high]
- status: one of [pending, in_progress, completed], default 'pending'
- due_date: ISO 8601 string, optional
- created_at: auto-generated ISO 8601
- updated_at: auto-updated ISO 8601

## Non-functional
- Listen on port 8080. Strict input validation and type checking. Complete error handling with the error envelope above. A health endpoint for monitoring.
========== END REQUIREMENT ==========

Output ONLY the Python code for main.py.
