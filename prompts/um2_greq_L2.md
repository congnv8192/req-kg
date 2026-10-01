You are a requirements analyst. Extract ONLY the structured information the requirement EXPLICITLY STATES or DIRECTLY IMPLIES. Do NOT invent details. Output STRICTLY a single JSON object in the schema below — no prose, no fences.

========== REQUIREMENT (Level L2) ==========
ProjectC is a RESTful API-based user management microservice that provides core functionality including user registration, login, information query, and updates. The service uses JWT tokens for authentication and supports CRUD operations on user data.

API Endpoints (base path /api/v1):
## API Definition

### Service Configuration
- **Protocol**: HTTP/HTTPS

### 1. User Registration API

**API Name**: `POST /api/v1/users/register`

### 2. User Login API

**API Name**: `POST /api/v1/users/login`

### 3. Get User Information API

**API Name**: `GET /api/v1/users/{user_id}`

### 4. Update User Information API

**API Name**: `PUT /api/v1/users/{user_id}`

### 5. Delete User API

**API Name**: `DELETE /api/v1/users/{user_id}`

Data model fields:
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
