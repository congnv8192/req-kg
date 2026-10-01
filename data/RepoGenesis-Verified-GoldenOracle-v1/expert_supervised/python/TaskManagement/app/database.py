"""
SQLite-backed storage layer.

A single, process-wide connection is used (guarded by a re-entrant lock) so
that the service works correctly regardless of whether the web framework
dispatches requests on the asyncio event loop or on a worker thread pool.
"""

import sqlite3
import threading
from contextlib import contextmanager
from typing import Iterator

from app.config import settings

_lock = threading.RLock()
_connection: "sqlite3.Connection | None" = None


_SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    priority TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    due_date TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
"""


def _create_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute(_SCHEMA)
    conn.commit()
    return conn


def get_connection() -> sqlite3.Connection:
    global _connection
    if _connection is None:
        with _lock:
            if _connection is None:
                _connection = _create_connection()
    return _connection


@contextmanager
def db_session() -> Iterator[sqlite3.Connection]:
    """Serialize access to the shared SQLite connection."""
    with _lock:
        yield get_connection()


def reset_database() -> None:
    """Drop and recreate all tables. Primarily useful for test isolation."""
    with _lock:
        conn = get_connection()
        conn.execute("DROP TABLE IF EXISTS tasks")
        conn.execute(_SCHEMA)
        conn.commit()
