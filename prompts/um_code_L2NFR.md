You are a senior backend engineer. Implement the microservice described below as a SINGLE self-contained Python file.

Hard constraints:
- Framework: FastAPI. Expose the app as module-level `app`.
- Runnable with `uvicorn main:app --host 127.0.0.1 --port 8081`. Include `if __name__ == "__main__":` running uvicorn on 127.0.0.1:8081.
- Base path prefix /api/v1. In-memory storage. Output ONLY the Python code — no fences, no explanation.

Implement EXACTLY what the requirement states — no more. If a constraint, error format, or validation rule is not specified, do NOT invent one.

========== REQUIREMENT (Level L2) ==========
A RESTful user management microservice: user CRUD, authentication, role and
status management, password reset. Supports pagination, filtering and search.

API (base path /api/v1):
- POST   /users                       create a user
- GET    /users                       list users (pagination, filtering, search)
- GET    /users/{id}                  retrieve a user
- PUT    /users/{id}                  update a user
- DELETE /users/{id}                  delete a user
- POST   /auth/login                  user login
- POST   /users/{id}/reset-password   reset a user's password
- GET    /health                      service health check

Data model — User:
  id, username, email, password_hash, full_name, role, phone, status, created_at, updated_at

List query parameters: page, limit, status, role, search.
========== END REQUIREMENT ==========

Non-functional requirements — implement each explicitly (this is the ONLY addition to the level-2 requirement; do NOT invent field-level constraints such as enum values or length limits that are not stated):
Technical specifications:
- **Framework**: Supports mainstream web frameworks (Flask, FastAPI, Django, etc.)
- **Database**: Supports relational databases (SQLite, PostgreSQL, MySQL, etc.)
- **Data Validation**: Strict input data validation and type checking
- **Error Handling**: Complete error handling and user-friendly error messages
- **Logging**: Complete operation logging, including security events
- **API Documentation**: Auto-generated API documentation (Swagger/OpenAPI)
- **Test Coverage**: Comprehensive unit tests and integration tests

Deployment requirements:
- **Port**: Service must listen on port 8081
- **Environment Variables**: Support configuration of database connections, JWT keys, etc. through environment variables
- **Health Check**: Provide health check endpoint for service monitoring
- **Containerization**: Support Docker containerized deployment
- **Database Migration**: Support database schema version management and migration
- **Configuration Management**: Support configuration management for different environments (development, testing, production)

Output ONLY the Python code for main.py.
