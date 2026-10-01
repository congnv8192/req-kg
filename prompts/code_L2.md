You are a senior backend engineer. Implement the microservice described by the requirement below as a SINGLE self-contained Python file.

Hard constraints (must follow exactly):
- Framework: FastAPI. Expose the app as a module-level variable named `app`.
- Runnable with: `uvicorn main:app --host 127.0.0.1 --port 8080`. Include an `if __name__ == "__main__":` block running uvicorn on 127.0.0.1:8080.
- Base path prefix: /api/v1 for all endpoints.
- Storage: in-memory. Output ONLY the Python source code — no fences, no explanation.

Implement EXACTLY what the requirement states — no more. If the requirement does not specify a constraint, an error format, or a validation rule, do NOT invent one.

========== REQUIREMENT (Level L2) ==========
A RESTful task management microservice providing task CRUD operations and status management. It supports pagination and filtering of tasks.

API (base path /api/v1):
- POST   /tasks         create a task
- GET    /tasks         list tasks (with pagination and filtering)
- GET    /tasks/{id}    retrieve a task
- PUT    /tasks/{id}    update a task
- DELETE /tasks/{id}    delete a task
- GET    /health        service health check

Data model — Task:
  id, title, description, priority, status, due_date, created_at, updated_at

List query parameters: page, limit, status, priority.
========== END REQUIREMENT ==========

Output ONLY the Python code for main.py.
