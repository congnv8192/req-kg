You are a requirements analyst. Read the software requirement below and extract ONLY the structured information that the requirement EXPLICITLY STATES or DIRECTLY IMPLIES. Do NOT invent details that are not supported by the text. If something is not mentioned, leave it out.

Output STRICTLY as a single JSON object in the schema shown after the requirement. No prose, no markdown fences — just the JSON.

========== REQUIREMENT (Level L2) ==========
A RESTful task management microservice providing task CRUD operations and status
management. It supports pagination and filtering of tasks.

API (base path /api/v1):
- POST   /tasks         create a task
- GET    /tasks         list tasks (with pagination and filtering)
- GET    /tasks/{id}    retrieve a task
- PUT    /tasks/{id}    update a task
- DELETE /tasks/{id}    delete a task
- GET    /health        service health check

Data model — Task:
  id, title, description, priority, status, due_date, created_at, updated_at

List query parameters: page, limit, status, priority.
========== END REQUIREMENT ==========

Output JSON schema (include a key only if the requirement supports it; use [] or null when nothing applies):
{
  "entities": ["<entity name>"],
  "attributes": [
    {"name":"<field>", "type":"<type or null>", "required":<true|false|null>,
     "max_length":<int or null>, "enum":[<values>] or null, "default":"<value or null>"}
  ],
  "operations": [
    {"method":"<GET|POST|PUT|DELETE or null>", "path":"<path or null>", "action":"<create|list|retrieve|update|delete|health|other>"}
  ],
  "relations": [{"from":"<entity>", "to":"<entity>", "kind":"<relation>"}],
  "thresholds": [{"name":"<e.g. port, max_page_size, default_page_size>", "value":<number or string>}],
  "nfr": [{"category":"<validation|error_handling|logging|health_check|deployment|configuration|api_docs|containerization>", "detail":"<short>"}]
}

Rules:
- Extract at the level of detail the requirement provides. L2 lists endpoints and field NAMES but NOT their constraints — do not invent max_length, enum values, or a port.
- The Task data model lists field names only; capture them as attributes with type/enum/max_length = null unless stated.
- Return ONLY the JSON object.
