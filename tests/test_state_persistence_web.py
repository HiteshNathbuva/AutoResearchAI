"""Phase 2 state/persistence: backward compatibility and migration."""

import sqlite3

from backend.core.session import SessionManager
from backend.core.state import WorkflowState


def test_old_state_loads_without_sources():
    # A pre-Phase-2 serialized dict has no sources/diagnostics keys.
    data = {
        "query": "topic", "plan": "plan", "research": "research",
        "verification": "", "final_report": "", "status": "Research completed",
        "confidence": "Unverified", "reading_time": 2, "current_step": "Research",
        "completed_tasks": ["Planner", "Research"],
        "created_at": "2020-01-01T00:00:00+00:00", "updated_at": "2020-01-01T00:00:00+00:00",
    }
    state = WorkflowState.from_dict(data)
    assert state.sources == []
    assert state.diagnostics == {}
    assert state.query == "topic"
    assert state.completed_tasks == ["Planner", "Research"]


def test_new_state_round_trips_sources_and_diagnostics():
    state = WorkflowState()
    state.update_query("rag")
    state.update_plan("plan")
    state.add_research_note("research")
    state.set_sources([{"source_id": 1, "url": "http://a.example/", "title": "A"}])
    state.set_diagnostics({"used_web": True, "search_status": "success"})

    restored = WorkflowState.from_dict(state.to_dict())

    assert restored.sources == state.sources
    assert restored.diagnostics == state.diagnostics
    assert restored.to_dict() == state.to_dict()


def test_sources_and_diagnostics_persist_through_session(tmp_path):
    manager = SessionManager(str(tmp_path / "mem.sqlite3"))
    state = WorkflowState()
    state.update_query("rag")
    state.set_sources([{"source_id": 1, "url": "http://a.example/", "title": "A"}])
    state.set_diagnostics({"used_web": True, "tool_mode": "enabled"})

    session_id = manager.create_session(state)
    loaded = manager.get_session(session_id)

    assert loaded.sources[0]["url"] == "http://a.example/"
    assert loaded.diagnostics["used_web"] is True


def test_old_sqlite_database_migrates_sources_and_diagnostics(tmp_path):
    """An existing Phase-1 database gains new columns without losing rows."""

    db_path = tmp_path / "old.sqlite3"
    connection = sqlite3.connect(db_path)
    # The exact Phase-1 schema (no sources/diagnostics columns).
    connection.execute("""CREATE TABLE research_sessions (
        id TEXT PRIMARY KEY, query TEXT NOT NULL, plan TEXT NOT NULL DEFAULT '',
        research TEXT NOT NULL DEFAULT '', verification TEXT NOT NULL DEFAULT '',
        final_report TEXT NOT NULL DEFAULT '', status TEXT NOT NULL, confidence TEXT,
        reading_time INTEGER, current_step TEXT NOT NULL,
        completed_tasks TEXT NOT NULL DEFAULT '[]', created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL)""")
    connection.execute("""INSERT INTO research_sessions
        (id, query, plan, research, verification, final_report, status, confidence,
         reading_time, current_step, completed_tasks, created_at, updated_at)
        VALUES ('old-1', 'old query', '', 'old research', '', '', 'Research completed',
        'Unverified', 2, 'Research', '["Planner","Research"]', '2020-01-01', '2020-01-01')""")
    connection.commit()
    connection.close()

    # Constructing the manager runs the idempotent migration.
    manager = SessionManager(str(db_path))

    # The old row is still readable and gained empty source/diagnostics fields.
    loaded = manager.get_session("old-1")
    assert loaded.query == "old query"
    assert loaded.research == "old research"
    assert loaded.sources == []
    assert loaded.diagnostics == {}

    # New columns exist and new rows can store sources/diagnostics.
    state = WorkflowState()
    state.update_query("new")
    state.set_sources([{"source_id": 1, "url": "http://new.example/", "title": "New"}])
    state.set_diagnostics({"used_web": True})
    new_id = manager.create_session(state)
    new_loaded = manager.get_session(new_id)
    assert new_loaded.sources[0]["url"] == "http://new.example/"
    assert new_loaded.diagnostics["used_web"] is True


def test_migration_is_idempotent(tmp_path):
    db_path = tmp_path / "idem.sqlite3"
    manager = SessionManager(str(db_path))
    # Run migration again --- must not error and must keep columns.
    with manager._connection() as connection:
        manager._migrate(connection)
    assert manager.get_session  # no error
