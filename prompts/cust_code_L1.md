You are a senior backend engineer. Implement the microservice described below as a SINGLE self-contained Python file.

Hard constraints:
- Framework: FastAPI. Expose the app as module-level `app`. Runnable with `uvicorn main:app --host 127.0.0.1 --port 8082`. Include `if __name__ == "__main__":` running uvicorn on 127.0.0.1:8082.
- Base path prefix /api/v1. In-memory storage. Output ONLY the Python code — no fences, no explanation.

Implement EXACTLY what the requirement states — no more. If a constraint, error format, or validation rule is not specified, do NOT invent one.

========== REQUIREMENT (Level L1) ==========
This is a personalization microservice API that provides user personalization management, including favorites, likes, and history tracking features. The service supports recording and managing user's personalized actions on content, helping to build a personalized user experience.
========== END REQUIREMENT ==========

Output ONLY the Python code for main.py.
