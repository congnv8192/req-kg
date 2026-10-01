You are a senior backend engineer. Implement the microservice described below as a SINGLE self-contained Python file.

Hard constraints:
- Framework: FastAPI. Expose the app as module-level `app`. Runnable with `uvicorn main:app --host 127.0.0.1 --port 8080`. Include `if __name__ == "__main__":` running uvicorn on 127.0.0.1:8080.
- Base path prefix /api/v1. In-memory storage. Output ONLY the Python code — no fences, no explanation.

Implement EXACTLY what the requirement states — no more. If a constraint, error format, or validation rule is not specified, do NOT invent one.

========== REQUIREMENT (Level L2) ==========
This service provides a simple API for implementing role-based access control. It allows creating roles, assigning permissions to roles, assigning roles to users, and checking user permissions.

API Endpoints (base path /api/v1):
## API Specification

The service runs on **port 8080** and provides the following REST APIs:

### 1. Create Role

**Endpoint**: `POST /api/roles`

**Description**: Create a new role in the system.

**Error Response**:

### 2. Assign Permission to Role

**Endpoint**: `POST /api/roles/{role_id}/permissions`

**Description**: Assign one or more permissions to a role.

**Error Response**:

### 3. Assign Role to User

**Endpoint**: `POST /api/users/{user_id}/roles`

**Description**: Assign one or more roles to a user.

**Error Response**:

### 4. Check User Permissions

**Endpoint**: `GET /api/users/{user_id}/permissions`

**Description**: Get all permissions for a user based on their assigned roles.

**Error Response**:

## Implementation Notes

- The service should persist data in memory (no database required for this benchmark)
- All responses should use JSON format
- HTTP status codes should follow REST conventions:
  - 200 OK for successful operations
  - 400 Bad Request for invalid input
  - 404 Not Found for non-existent resources
  - 500 Internal Server Error for server errors
- Role IDs and User IDs should be handled as strings
- Permission names are case-sensitive
- A user can have multiple roles
- A role can have multiple permissions
- Permissions from multiple roles are combined (union)

Data model fields:
- **Role**: A named role (e.g., "admin", "editor", "viewer")
- **Permission**: A named permission (e.g., "read", "write", "delete")
- **User**: A user identified by user_id with assigned roles
========== END REQUIREMENT ==========

Output ONLY the Python code for main.py.
