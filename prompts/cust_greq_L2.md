You are a requirements analyst. Extract ONLY the structured information the requirement EXPLICITLY STATES or DIRECTLY IMPLIES. Do NOT invent details. Output STRICTLY a single JSON object in the schema below — no prose, no fences.

========== REQUIREMENT (Level L2) ==========
This is a personalization microservice API that provides user personalization management, including favorites, likes, and history tracking features. The service supports recording and managing user's personalized actions on content, helping to build a personalized user experience.

API Endpoints (base path /api/v1):
## API Definition

### Service Configuration

### 1. Favorites Management APIs

#### 1.1 Add Favorite
- **API Name**: `POST /api/v1/favorites`
- **Function**: User adds content to favorites
- **Authentication**: Bearer Token required

#### 1.2 Get Favorites List
- **API Name**: `GET /api/v1/favorites`
- **Function**: Retrieve user's favorites list, supports pagination and filtering
- **Authentication**: Bearer Token required
  - `page`: integer (default 1)
  - `limit`: integer (default 10, max 100)
  - `content_type`: string (filter by content type)
  - `category`: string (filter by category label)

#### 1.3 Delete Favorite
- **API Name**: `DELETE /api/v1/favorites/{favorite_id}`
- **Function**: Delete a specific favorite record
- **Authentication**: Bearer Token required

### 2. Likes Management APIs

#### 2.1 Add Like
- **API Name**: `POST /api/v1/likes`
- **Function**: User performs a like/unlike action on content
- **Authentication**: Bearer Token required

#### 2.2 Get Like Stats
- **API Name**: `GET /api/v1/likes/stats/{content_id}`
- **Function**: Retrieve like statistics for specific content
- **Authentication**: Optional

#### 2.3 Get User Like History
- **API Name**: `GET /api/v1/likes/history`
- **Function**: Retrieve user's like action history
- **Authentication**: Bearer Token required
  - `page`: integer (default 1)
  - `limit`: integer (default 10, max 50)
  - `content_type`: string (filter by content type)

### 3. History APIs

#### 3.1 Record User Action
- **API Name**: `POST /api/v1/history`
- **Function**: Record a user's action history
- **Authentication**: Bearer Token required

#### 3.2 Get History Records
- **API Name**: `GET /api/v1/history`
- **Function**: Retrieve user's history records with various filters
- **Authentication**: Bearer Token required
  - `page`: integer (default 1)
  - `limit`: integer (default 20, max 100)
  - `action`: string (filter by action type)
  - `content_type`: string (filter by content type)
  - `session_id`: string (filter by session)

#### 3.3 Delete History Record
- **API Name**: `DELETE /api/v1/history/{history_id}`
- **Function**: Delete a specific history record
- **Authentication**: Bearer Token required

#### 3.4 Clear History Records
- **API Name**: `DELETE /api/v1/history`
- **Function**: Clear all history records for the user
- **Authentication**: Bearer Token required

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
