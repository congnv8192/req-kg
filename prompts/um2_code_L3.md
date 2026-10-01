You are a senior backend engineer. Implement the microservice described below as a SINGLE self-contained Python file.

Hard constraints:
- Framework: FastAPI. Expose the app as module-level `app`. Runnable with `uvicorn main:app --host 127.0.0.1 --port 8080`. Include `if __name__ == "__main__":` running uvicorn on 127.0.0.1:8080.
- Base path prefix /api/v1. In-memory storage. Output ONLY the Python code — no fences, no explanation.

Implement EXACTLY what the requirement states — no more. If a constraint, error format, or validation rule is not specified, do NOT invent one.

========== REQUIREMENT (Level L3) ==========
# ProjectC - User Management Microservice

## Functionality Description

ProjectC is a RESTful API-based user management microservice that provides core functionality including user registration, login, information query, and updates. The service uses JWT tokens for authentication and supports CRUD operations on user data.

## API Definition

### Service Configuration
- **Listening Port**: 8080
- **Base Path**: `/api/v1`
- **Protocol**: HTTP/HTTPS

### 1. User Registration API

**API Name**: `POST /api/v1/users/register`

**Input Schema**:
```json
{
  "username": "string (required, 3-20 characters)",
  "email": "string (required, valid email format)",
  "password": "string (required, 6-50 characters)",
  "full_name": "string (optional, max 100 characters)"
}
```

**Output Schema**:
```json
{
  "success": "boolean",
  "message": "string",
  "data": {
    "user_id": "integer",
    "username": "string",
    "email": "string",
    "full_name": "string",
    "created_at": "string (ISO 8601 format)"
  }
}
```

### 2. User Login API

**API Name**: `POST /api/v1/users/login`

**Input Schema**:
```json
{
  "username": "string (required)",
  "password": "string (required)"
}
```

**Output Schema**:
```json
{
  "success": "boolean",
  "message": "string",
  "data": {
    "access_token": "string (JWT token)",
    "token_type": "string (fixed value: 'Bearer')",
    "expires_in": "integer (seconds)",
    "user": {
      "user_id": "integer",
      "username": "string",
      "email": "string",
      "full_name": "string"
    }
  }
}
```

### 3. Get User Information API

**API Name**: `GET /api/v1/users/{user_id}`

**Headers**:
```
Authorization: Bearer <access_token>
```

**Output Schema**:
```json
{
  "success": "boolean",
  "message": "string",
  "data": {
    "user_id": "integer",
    "username": "string",
    "email": "string",
    "full_name": "string",
    "created_at": "string (ISO 8601 format)",
    "updated_at": "string (ISO 8601 format)"
  }
}
```

### 4. Update User Information API

**API Name**: `PUT /api/v1/users/{user_id}`

**Headers**:
```
Authorization: Bearer <access_token>
```

**Input Schema**:
```json
{
  "email": "string (optional, valid email format)",
  "full_name": "string (optional, max 100 characters)"
}
```

**Output Schema**:
```json
{
  "success": "boolean",
  "message": "string",
  "data": {
    "user_id": "integer",
    "username": "string",
    "email": "string",
    "full_name": "string",
    "updated_at": "string (ISO 8601 format)"
  }
}
```

### 5. Delete User API

**API Name**: `DELETE /api/v1/users/{user_id}`

**Headers**:
```
Authorization: Bearer <access_token>
```

**Output Schema**:
```json
{
  "success": "boolean",
  "message": "string"
}
```

## Error Response Format

All interfaces return unified format when errors occur:

```json
{
  "success": false,
  "message": "string (error description)",
  "error_code": "string (error code)",
  "details": "object (optional, detailed error information)"
}
```

## Technology Stack Requirements
- Python 3.8+
- FastAPI/Flask framework
- JWT token authentication
- SQLite/PostgreSQL database
- Pytest testing framework

## Deployment Requirements
- Containerized deployment support
- Environment variable configuration
- Logging
- Health check endpoint
========== END REQUIREMENT ==========

Output ONLY the Python code for main.py.
