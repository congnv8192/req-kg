# TaskManagement — SRS cắt theo mức L1/L2/L3 (taxonomy Zi et al.)

Repo: RepoGenesis expert-supervised / TaskManagement (Gemini-oracle).
Nguồn L3 = README gốc (SRS ~80% IEEE 830). Cắt xuống L2/L1 theo **taxonomy 4-nhóm
Zi et al. (PartialOrderEval)**, KHÔNG viết lại — chỉ rút gọn có quy tắc.

Quy tắc cắt:
- **L3** = README đầy đủ: functionality + API schema + data model + error + Technical Spec + Deployment. = taxonomy nhóm 1+2+3+4 (gồm khối NFR).
- **L2** = giữ nhóm 1 (Functional: mục tiêu + API + data model) + tên endpoint; BỎ nhóm 2-3 chi tiết (constraint đầy đủ, enum liệt kê, error format) + BỎ khối NFR (Technical Spec, Deployment).
- **L1** = chỉ nhóm 1.1 (Task Goal): 1 đoạn Functionality Description.

Đây là INPUT cho Pha A (LLM sinh G_req từ mỗi mức) và cho annotator mù (kiểm L1<L2<L3, kappa).

---

## L3 — README đầy đủ (KHÔNG cắt)

= file gốc `data/RepoGenesis-Verified-GoldenOracle-v1/expert_supervised/python/TaskManagement/README.md`
Chứa toàn bộ: 6 API (CRUD + list + health) với input/output schema; Error Response Format
(400/404/422/500); Data Model (Task với 8 field + constraint + enum + default); Technical
Specifications (validation, error-handling, logging, API docs); Deployment Requirements
(port 8080, env vars, health check, Docker).

[Tham chiếu file gốc — không sao chép để giữ nguyên vẹn; xem TERMS_OF_USE oracle.]

---

## L2 — giữ Functional + API + data model; BỎ constraint chi tiết + NFR block

Task management microservice: RESTful API cho quản lý task (tạo, xem, cập nhật, xóa),
có phân trang và lọc theo trạng thái/độ ưu tiên.

API Endpoints (base /api/v1):
- POST   /tasks           — tạo task
- GET    /tasks           — liệt kê task (phân trang, lọc)
- GET    /tasks/{id}      — lấy 1 task
- PUT    /tasks/{id}      — cập nhật task
- DELETE /tasks/{id}      — xóa task
- GET    /health          — kiểm tra sức khỏe dịch vụ

Data Model — Task:
- id, title, description, priority, status, due_date, created_at, updated_at

Query (list): page, limit, status, priority.

[BỎ so với L3: giá trị enum liệt kê (['low','medium','high']...), max-length cụ thể
(200/1000), default 'pending', ISO-8601 format, Error Response Format chi tiết,
và TOÀN BỘ khối NFR — Technical Spec + Deployment Requirements.]

---

## L1 — chỉ Task Goal (1 đoạn)

A RESTful task management microservice providing CRUD operations and status
management for tasks.

[BỎ so với L2: liệt kê endpoint tường minh, data model, query params, health-check.]

**Lưu ý ngụ ý (khớp G_REQ script):** câu goal chứa "CRUD operations" → NGỤ Ý được
5 endpoint CRUD (create/list/get/update/delete task) — nên G_req(L1) có chúng.
NHƯNG `health_check` KHÔNG suy ra được từ goal → L1 không có (chỉ hiện ở L2 khi
liệt kê endpoint). Đây là ranh giới "suy diễn được" vs "phải nêu tường minh".

---

## Bảng "khoảng ngầm" (Gap = L3 \ Lx) theo taxonomy — dự kiến

Luật trong L3 (code cần) mà L1/L2 BỎ:

| Luật ngầm | Ở L3? | L2 bỏ? | L1 bỏ? | Nhóm taxonomy | Loại |
|---|---|---|---|---|---|
| priority ∈ {low,medium,high} | ✅ | BỎ | BỎ | 2 Constraints | enum (declarative) |
| status ∈ {pending,in_progress,completed} | ✅ | BỎ | BỎ | 2 Constraints | enum (declarative) |
| status default = 'pending' | ✅ | BỎ | BỎ | 2 Constraints | default value |
| title max 200 / description max 1000 | ✅ | BỎ | BỎ | 2 Constraints | threshold |
| due_date ISO-8601 | ✅ | BỎ | BỎ | 2 Constraints | format (procedural) |
| pagination limit default 10 / max 100 | ✅ | giữ(tên) | BỎ | 2 Constraints | threshold |
| error format 400/404/422/500 | ✅ | BỎ | BỎ | 4 Integration | contract |
| validation / error-handling (NFR-struct) | ✅ | BỎ | BỎ | 5 NFR-structural | file/module |
| health-check endpoint | ✅ | giữ | BỎ | 5 NFR (observability) | endpoint |
| port 8080 / env-config / Docker | ✅ | BỎ | BỎ | 5 NFR (deployment) | config |

→ **NFR (nhóm 5) bị bỏ SẠCH ở L1 (=0), chỉ hiện dần ở L2-L3** — khớp phát hiện
NFR-coverage 0.00→0.38→1.00. Constraint (nhóm 2) bỏ sớm & dai dẳng.

---

*Cắt theo taxonomy Zi et al. · L3=README gốc, L2/L1 rút gọn có quy tắc · không viết lại.
INPUT cho Pha A (LLM sinh G_req) + annotator mù (kappa L1<L2<L3).*
