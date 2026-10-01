You are a requirements analyst. Read the software requirement below and extract ONLY the structured information that the requirement EXPLICITLY STATES or DIRECTLY IMPLIES. Do NOT invent details that are not supported by the text. If something is not mentioned, leave it out.

Output STRICTLY as a single JSON object in the schema shown after the requirement. No prose, no markdown fences — just the JSON.

========== REQUIREMENT (Level L1) ==========
This is a RESTful API-based task management microservice that provides complete
task CRUD operations and status management functionality. The service allows
users to create, view, update, and delete tasks, while supporting task status
tracking and priority management.
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
- Extract at the level of detail the requirement provides. L1 is a short description — expect few, coarse elements.
- "CRUD operations" implies create/list/retrieve/update/delete actions even if endpoints are not spelled out.
- Do NOT add constraints (max_length, enum, port...) unless the text states them.
- Return ONLY the JSON object.
