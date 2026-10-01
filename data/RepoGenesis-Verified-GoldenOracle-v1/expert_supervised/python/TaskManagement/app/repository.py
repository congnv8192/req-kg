"""
Data access layer for tasks. All SQL lives here; the API layer only deals
with plain Python dictionaries.
"""

import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.database import db_session

_UPDATABLE_FIELDS = ("title", "description", "priority", "status", "due_date")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + \
        f"{datetime.now(timezone.utc).microsecond // 1000:03d}Z"


def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "priority": row["priority"],
        "status": row["status"],
        "due_date": row["due_date"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def create_task(data: Dict[str, Any]) -> Dict[str, Any]:
    now = _utc_now_iso()
    with db_session() as conn:
        cursor = conn.execute(
            """
            INSERT INTO tasks
                (title, description, priority, status, due_date, created_at, updated_at)
            VALUES (?, ?, ?, 'pending', ?, ?, ?)
            """,
            (
                data["title"],
                data.get("description"),
                data["priority"],
                data.get("due_date"),
                now,
                now,
            ),
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return _row_to_dict(row)


def get_task(task_id: int) -> Optional[Dict[str, Any]]:
    with db_session() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return _row_to_dict(row) if row is not None else None


def list_tasks(
    page: int,
    limit: int,
    status: Optional[str] = None,
    priority: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], int]:
    conditions = []
    params: List[Any] = []
    if status is not None:
        conditions.append("status = ?")
        params.append(status)
    if priority is not None:
        conditions.append("priority = ?")
        params.append(priority)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    with db_session() as conn:
        total_row = conn.execute(
            f"SELECT COUNT(*) AS cnt FROM tasks {where_clause}", params
        ).fetchone()
        total = total_row["cnt"]

        offset = (page - 1) * limit
        rows = conn.execute(
            f"SELECT * FROM tasks {where_clause} ORDER BY id ASC LIMIT ? OFFSET ?",
            params + [limit, offset],
        ).fetchall()

        return [_row_to_dict(r) for r in rows], total


def update_task(task_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    with db_session() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if row is None:
            return None

        current = _row_to_dict(row)
        for field in _UPDATABLE_FIELDS:
            if field in data:
                current[field] = data[field]

        now = _utc_now_iso()
        conn.execute(
            """
            UPDATE tasks
            SET title = ?, description = ?, priority = ?, status = ?, due_date = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                current["title"],
                current["description"],
                current["priority"],
                current["status"],
                current["due_date"],
                now,
                task_id,
            ),
        )
        conn.commit()
        current["updated_at"] = now
        return current


def delete_task(task_id: int) -> bool:
    with db_session() as conn:
        cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        return cursor.rowcount > 0


def delete_all_tasks() -> None:
    with db_session() as conn:
        conn.execute("DELETE FROM tasks")
        conn.commit()
