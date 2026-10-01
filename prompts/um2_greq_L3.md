You are a requirements analyst. Extract ONLY the structured information the requirement EXPLICITLY STATES or DIRECTLY IMPLIES. Do NOT invent details. Output STRICTLY a single JSON object in the schema below — no prose, no fences.

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

Schema (include a key only if supported; use [] or null when nothing applies):
{
  "entities": ["<entity>"],
  "attributes": [{"name":"<field>","type":"<type|null>","required":<bool|null>,"max_length":<int|null>,"min_length":<int|null>,"enum":[<values>]|null,"default":"<value|null>","unique":<bool|null>}],
  "operations": [{"method":"<GET|POST|PUT|DELETE|null>","path":"<path|null>","action":"<create|list|retrieve|update|delete|login|reset_password|health|other>"}],
  "relations": [{"from":"<entity>","to":"<entity>","kind":"<relation>"}],
  "thresholds": [{"name":"<e.g. port, max_page_size>","value":<number|string>}],
  "nfr": [{"category":"<validation|error_handling|logging|health_check|deployment|configuration|containerization|auth|migration>","detail":"<short>"}]
}

Rules: extract at the level of detail the requirement provides. Do NOT add constraints (enum, lengths, port) unless the text states them. Return ONLY the JSON.
