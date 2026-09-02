"""Session persistence: CRUD, listing, connection lifecycle, and schema."""

import os
import sqlite3
import threading

import pytest

from backend.core.session import SessionManager
from backend.core.state import WorkflowState


def _state(query: str = "topic") -> WorkflowState:
    state = WorkflowState()
    state.update_query(query)
    return state


def test_create_and_get_session_round_trip(session_manager: SessionManager):
    state = _state("agentic workflows")
    state.update_plan("plan")
    state.add_research_note("research")
    state.set_reading_time(3)

    session_id = session_manager.create_session(state)
    loaded = session_manager.get_session(session_id)

    assert session_id
    assert loaded.query == "agentic workflows"
    assert loaded.plan == "plan"
    assert loaded.research == "research"
    assert loaded.reading_time == 3


def test_get_missing_session_raises_key_error(session_manager: SessionManager):
    with pytest.raises(KeyError):
        session_manager.get_session("does-not-exist")


def test_update_session_persists_changes(session_manager: SessionManager):
    session_id = session_manager.create_session(_state())

    state = session_manager.get_session(session_id)
    state.set_final_report("the final report")
    state.update_status("Report generated")
    state.set_confidence("High")
    session_manager.update_session(session_id, state)

    reloaded = session_manager.get_session(session_id)
    assert reloaded.final_report == "the final report"
    assert reloaded.status == "Report generated"
    assert reloaded.confidence == "High"


def test_update_session_preserves_created_at(session_manager: SessionManager):
    session_id = session_manager.create_session(_state())
    created_at = session_manager.get_session(session_id).metadata["created_at"]

    state = session_manager.get_session(session_id)
    state.update_status("Verifying")
    session_manager.update_session(session_id, state)

    assert session_manager.get_session(session_id).metadata["created_at"] == created_at


def test_update_missing_session_raises_key_error(session_manager: SessionManager):
    with pytest.raises(KeyError):
        session_manager.update_session("does-not-exist", _state())


def test_list_sessions_is_ordered_and_flags_reports(session_manager: SessionManager):
    first = session_manager.create_session(_state("first"))

    with_report = _state("second")
    with_report.set_final_report("report body")
    second = session_manager.create_session(with_report)

    rows = session_manager.list_sessions()
    ids = [row["id"] for row in rows]

    assert set(ids) == {first, second}
    assert rows == sorted(rows, key=lambda row: row["updated_at"], reverse=True)

    by_id = {row["id"]: row for row in rows}
    assert bool(by_id[second]["has_report"]) is True
    assert bool(by_id[first]["has_report"]) is False


def test_list_sessions_respects_limit(session_manager: SessionManager):
    for index in range(5):
        session_manager.create_session(_state(f"query {index}"))
    assert len(session_manager.list_sessions(limit=2)) == 2


def test_list_sessions_does_not_return_report_bodies(session_manager: SessionManager):
    state = _state()
    state.set_final_report("secret body")
    session_manager.create_session(state)

    row = session_manager.list_sessions()[0]
    assert "final_report" not in row
    assert "secret body" not in str(row.values())


def test_connections_are_closed(session_manager: SessionManager):
    """Regression test for the connection/file-descriptor leak."""

    fd_dir = "/proc/self/fd"
    if not os.path.isdir(fd_dir):
        pytest.skip("file descriptor introspection unavailable")

    for index in range(20):
        session_manager.create_session(_state(f"warmup {index}"))
    baseline = len(os.listdir(fd_dir))

    for index in range(100):
        session_id = session_manager.create_session(_state(f"query {index}"))
        session_manager.get_session(session_id)
        session_manager.list_sessions(limit=1)

    assert len(os.listdir(fd_dir)) <= baseline + 5


def test_wal_mode_and_index_are_configured(session_manager: SessionManager):
    connection = sqlite3.connect(session_manager.database_path)
    try:
        mode = connection.execute("PRAGMA journal_mode").fetchone()[0]
        indexes = [row[1] for row in connection.execute(
            "PRAGMA index_list('research_sessions')").fetchall()]
    finally:
        connection.close()

    assert mode.lower() == "wal"
    assert "idx_research_sessions_updated_at" in indexes


def test_database_file_and_parent_are_created(tmp_path):
    database_path = tmp_path / "nested" / "dir" / "sessions.sqlite3"
    manager = SessionManager(str(database_path))
    manager.create_session(_state())
    assert database_path.exists()


def test_concurrent_writes_are_serialized(session_manager: SessionManager):
    errors = []

    def worker(index: int):
        try:
            session_manager.create_session(_state(f"concurrent {index}"))
        except Exception as error:  # pragma: no cover - failure path
            errors.append(error)

    threads = [threading.Thread(target=worker, args=(index,)) for index in range(10)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert errors == []
    assert len(session_manager.list_sessions(limit=100)) == 10
