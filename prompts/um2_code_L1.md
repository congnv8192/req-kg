You are a senior backend engineer. Implement the microservice described below as a SINGLE self-contained Python file.

Hard constraints:
- Framework: FastAPI. Expose the app as module-level `app`. Runnable with `uvicorn main:app --host 127.0.0.1 --port 8080`. Include `if __name__ == "__main__":` running uvicorn on 127.0.0.1:8080.
- Base path prefix /api/v1. In-memory storage. Output ONLY the Python code — no fences, no explanation.

Implement EXACTLY what the requirement states — no more. If a constraint, error format, or validation rule is not specified, do NOT invent one.

========== REQUIREMENT (Level L1) ==========
ProjectC is a RESTful API-based user management microservice that provides core functionality including user registration, login, information query, and updates. The service uses JWT tokens for authentication and supports CRUD operations on user data.
========== END REQUIREMENT ==========

Output ONLY the Python code for main.py.
