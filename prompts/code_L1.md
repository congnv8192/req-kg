You are a senior backend engineer. Implement the microservice described by the requirement below as a SINGLE self-contained Python file.

Hard constraints (must follow exactly):
- Framework: FastAPI. Expose the app as a module-level variable named `app`.
- Runnable with: `uvicorn main:app --host 127.0.0.1 --port 8080`. Include an `if __name__ == "__main__":` block running uvicorn on 127.0.0.1:8080.
- Base path prefix: /api/v1 for all endpoints.
- Storage: in-memory. Output ONLY the Python source code — no fences, no explanation.

Implement EXACTLY what the requirement states — no more. The requirement is brief; do NOT invent endpoints, fields, constraints, or error formats it does not mention. Make reasonable minimal choices only where strictly needed to run.

========== REQUIREMENT (Level L1) ==========
This is a RESTful API-based task management microservice that provides complete
task CRUD operations and status management functionality. The service allows
users to create, view, update, and delete tasks, while supporting task status
tracking and priority management.
========== END REQUIREMENT ==========

Output ONLY the Python code for main.py.
