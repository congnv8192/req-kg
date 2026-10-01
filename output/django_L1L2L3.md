# T3 — Cắt README (L3) → L2 → L1 theo taxonomy Zi et al.

Case: django-rest-framework-crud (JWT movie management)

## L3 = README gốc (đầy đủ) — KHÔNG cắt
Chứa: functionality + auth flow + toàn bộ API endpoint + input/output schema chi tiết
(field, kiểu, required, pagination, fuzzy filter). = taxonomy nhóm 1+2+3+4.
[= file repogen_django_README.md, 102 dòng]

---

## L2 = giữ nhóm 1 (Functional) + tên API; BỎ nhóm 2-3 (schema chi tiết, constraint)

Web Microservice: JWT-based movie resource management.
Unauthenticated users cannot access movies. Authenticated users can
create, query, update, delete their own movies, with title filtering
and pagination.

API Endpoints (port 8000, prefix /api/v1):
- POST /auth/register/  — register user
- POST /auth/token/     — login, get JWT
- POST /auth/refresh/   — refresh token
- GET  /movies/         — list movies (filter, paginate)
- POST /movies/         — create movie
- GET  /movies/{id}/    — get movie
- PUT  /movies/{id}/    — update movie
- DELETE /movies/{id}/  — delete movie

Entities: User, Movie (belongs to a creator User).

[BỎ so với L3: input/output schema chi tiết, kiểu field, max-length,
 required/optional, mã lỗi, status code — các "luật" nhóm 2-3]

---

## L1 = chỉ nhóm 1.1 (Task Goal) — 1-2 câu

A JWT-secured REST microservice for managing personal movie records
(CRUD) with authentication.

[BỎ so với L2: danh sách API, entity, auth flow chi tiết]

---

## Phân loại "khoảng ngầm" (Gap = L3 \ Lx) theo taxonomy

Luật trong L3 (code cần) mà L1/L2 BỎ:

| Luật ngầm | Có ở L3? | L2 bỏ? | L1 bỏ? | Nhóm taxonomy |
|---|---|---|---|---|
| "movie thuộc về creator (ownership)" | ✅ | giữ | BỎ | 1.5 Core Behaviour |
| "chỉ owner sửa/xóa được" (IsOwnerOrReadOnly) | ✅ | BỎ | BỎ | 2.5 Data Invariant / 2.4 Auth |
| "title fuzzy filter" | ✅ | giữ(tên) | BỎ | 1.5 Core Behaviour |
| "pagination default/limit" | ✅ | giữ(tên) | BỎ | 1.3 Input Spec |
| "password2 confirm khớp password" | ✅ | BỎ | BỎ | 2.3 Edge / 2.4 Validation |
| "field year là PositiveInteger" | ✅ | BỎ | BỎ | 1.3 Input Spec |
| "JWT access + refresh token" | ✅ | giữ | BỎ | 2.2 Environment |

→ L1→L2→L3: khoảng ngầm THU HẸP dần. Loại nhóm 2 (constraint/validation)
  bị bỏ SỚM (ngay L2) và DAI DẲNG — đây là "luật ngầm" điển hình.
