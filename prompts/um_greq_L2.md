You are a requirements analyst. Extract ONLY the structured information the requirement EXPLICITLY STATES or DIRECTLY IMPLIES. Do NOT invent details. Output STRICTLY a single JSON object in the schema below — no prose, no fences.

========== REQUIREMENT (Level L2) ==========
A RESTful user management microservice: user CRUD, authentication, role and
status management, password reset. Supports pagination, filtering and search.

API (base path /api/v1):
- POST   /users                       create a user
- GET    /users                       list users (pagination, filtering, search)
- GET    /users/{id}                  retrieve a user
- PUT    /users/{id}                  update a user
- DELETE /users/{id}                  delete a user
- POST   /auth/login                  user login (authentication)
- POST   /users/{id}/reset-password   reset a user's password
- GET    /health                      service health check

Data model — User:
  id, username, email, password_hash, full_name, role, phone, status, created_at, updated_at

List query parameters: page, limit, status, role, search.
========== END REQUIREMENT ==========

Schema (include a key only if supported; use [] or null when nothing applies):
{
  "entities": ["<entity>"],
  "attributes": [{"name":"<field>","type":"<type|null>","required":<bool|null>,"max_length":<int|null>,"min_length":<int|null>,"enum":[<values>]|null,"default":"<value|null>"}],
  "operations": [{"method":"<GET|POST|PUT|DELETE|null>","path":"<path|null>","action":"<create|list|retrieve|update|delete|login|reset_password|health|other>"}],
  "relations": [{"from":"<entity>","to":"<entity>","kind":"<relation>"}],
  "thresholds": [{"name":"<...>","value":<number|string>}],
  "nfr": [{"category":"<validation|error_handling|logging|health_check|deployment|configuration|containerization|auth|migration>","detail":"<short>"}]
}

Rules: L2 lists endpoints and field NAMES but NOT their constraints — do not invent enum values, lengths, or a port. Capture fields as attributes with type/enum/length = null unless stated. Return ONLY the JSON.
