You are a senior backend engineer. Implement the microservice described below as a SINGLE self-contained Python file.

Hard constraints:
- Framework: FastAPI. Expose the app as module-level `app`. Runnable with `uvicorn main:app --host 127.0.0.1 --port 8082`. Include `if __name__ == "__main__":` running uvicorn on 127.0.0.1:8082.
- Base path prefix /api/v1. In-memory storage. Output ONLY the Python code — no fences, no explanation.

Implement EXACTLY what the requirement states — no more. If a constraint, error format, or validation rule is not specified, do NOT invent one.

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

Non-functional requirements — implement each explicitly (this is the ONLY addition to the level-2 requirement; do NOT invent field-level constraints such as enum values or length limits that are not stated):
Non-functional: strict input validation; unified error envelope with proper HTTP codes; health check endpoint; listen on port 8082; environment-variable configuration; containerization.

Output ONLY the Python code for main.py.
