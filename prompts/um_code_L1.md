You are a senior backend engineer. Implement the microservice described below as a SINGLE self-contained Python file.

Hard constraints:
- Framework: FastAPI. Expose the app as module-level `app`.
- Runnable with `uvicorn main:app --host 127.0.0.1 --port 8081`. Include `if __name__ == "__main__":` running uvicorn on 127.0.0.1:8081.
- Base path prefix /api/v1 for all endpoints. In-memory storage. Output ONLY the Python code — no fences, no explanation.

Implement EXACTLY what the requirement states — no more. It is brief; do NOT invent endpoints, fields, constraints, or error formats it does not mention. Make minimal choices only where strictly needed to run.

========== REQUIREMENT (Level L1) ==========
This is a RESTful API-based user management microservice that provides complete
user CRUD operations, authentication, and permission management functionality.
The service allows administrators to create, view, update, and delete user
accounts, while supporting user status management, role assignment, and
password reset functionality.
========== END REQUIREMENT ==========

Output ONLY the Python code for main.py.
