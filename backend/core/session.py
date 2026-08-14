"""SQLite-backed persistence for research sessions."""

import json
import sqlite3
import threading
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.core.config import get_settings
from backend.core.logger import get_logger
from backend.core.state import WorkflowState

logger = get_logger(__name__)

BUSY_TIMEOUT_MS = 5000

CREATE_TABLE_SQL = """CREATE TABLE IF NOT EXISTS research_sessions (
    id TEXT PRIMARY KEY, query TEXT NOT NULL, plan TEXT NOT NULL DEFAULT '',
    research TEXT NOT NULL DEFAULT '', verification TEXT NOT NULL DEFAULT '',
    final_report TEXT NOT NULL DEFAULT '', status TEXT NOT NULL, confidence TEXT,
    reading_time INTEGER, current_step TEXT NOT NULL,
    completed_tasks TEXT NOT NULL DEFAULT '[]', created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL)"""

CREATE_INDEX_SQL = (
    "CREATE INDEX IF NOT EXISTS idx_research_sessions_updated_at "
    "ON research_sessions (updated_at DESC)"
)


class SessionManager:
    """Persist workflow state so reports and history survive server restarts."""

    def __init__(self, database_path: Optional[str] = None):
        self.database_path = Path(database_path or get_settings().DATABASE_PATH)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._initialize_database()

    @contextmanager
    def _connection(self):
        """Yield a configured connection and always close it."""

        connection = sqlite3.connect(self.database_path, check_same_thread=False,
                                     timeout=BUSY_TIMEOUT_MS / 1000)
        connection.row_factory = sqlite3.Row
        try:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute(f"PRAGMA busy_timeout={BUSY_TIMEOUT_MS}")
            connection.execute("PRAGMA foreign_keys=ON")
            with connection:
                yield connection
        finally:
            connection.close()

    def _initialize_database(self) -> None:
        with self._lock, self._connection() as connection:
            connection.execute(CREATE_TABLE_SQL)
            connection.execute(CREATE_INDEX_SQL)

    @staticmethod
    def _state_values(session_id: str, state: WorkflowState):
        data = state.to_dict()
        return (session_id, data["query"], data["plan"], data["research"],
                data["verification"], data["final_report"], data["status"],
                data["confidence"], data["reading_time"], data["current_step"],
                json.dumps(data["completed_tasks"]), data["created_at"], data["updated_at"])

    @staticmethod
    def _row_to_state(row: sqlite3.Row) -> WorkflowState:
        return WorkflowState.from_dict({
            "query": row["query"], "plan": row["plan"], "research": row["research"],
            "verification": row["verification"], "final_report": row["final_report"],
            "status": row["status"], "confidence": row["confidence"],
            "reading_time": row["reading_time"], "current_step": row["current_step"],
            "completed_tasks": json.loads(row["completed_tasks"]),
            "created_at": row["created_at"], "updated_at": row["updated_at"]})

    def create_session(self, state: WorkflowState) -> str:
        session_id = str(uuid.uuid4())
        with self._lock, self._connection() as connection:
            connection.execute("""INSERT INTO research_sessions
                (id, query, plan, research, verification, final_report, status, confidence,
                 reading_time, current_step, completed_tasks, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                self._state_values(session_id, state))
        return session_id

    def get_session(self, session_id: str) -> WorkflowState:
        with self._lock, self._connection() as connection:
            row = connection.execute("SELECT * FROM research_sessions WHERE id = ?",
                                     (session_id,)).fetchone()
        if row is None:
            raise KeyError(session_id)
        return self._row_to_state(row)

    def update_session(self, session_id: str, state: WorkflowState) -> None:
        values = self._state_values(session_id, state)
        with self._lock, self._connection() as connection:
            cursor = connection.execute("""UPDATE research_sessions SET query=?, plan=?, research=?,
                verification=?, final_report=?, status=?, confidence=?, reading_time=?, current_step=?,
                completed_tasks=?, updated_at=? WHERE id=?""",
                (*values[1:11], values[12], session_id))
        if cursor.rowcount == 0:
            raise KeyError(session_id)

    def list_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._lock, self._connection() as connection:
            rows = connection.execute("""SELECT id, query, status, confidence, reading_time,
                created_at, updated_at, (final_report != '') AS has_report
                FROM research_sessions ORDER BY updated_at DESC LIMIT ?""", (limit,)).fetchall()
        return [dict(row) for row in rows]
