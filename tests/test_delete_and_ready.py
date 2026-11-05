"""Tests for session deletion and the readiness endpoint."""

from backend.core.state import WorkflowState


def _make_state(query="Test query about AI"):
    state = WorkflowState(query)
    state.update_plan("plan")
    state.add_research_note("research notes with some content here")
    state.set_final_report("# Report\n\nBody text.")
    state.mark_task_complete("Planner")
    return state


def test_delete_session(client, session_manager):
    session_id = session_manager.create_session(_make_state())
    response = client.delete(f"/api/sessions/{session_id}")
    assert response.status_code == 204
    listing = client.get("/api/sessions").json()["sessions"]
    assert all(s["session_id"] != session_id for s in listing)


def test_delete_unknown_session(client):
    response = client.delete("/api/sessions/does-not-exist")
    assert response.status_code == 404


def test_ready_endpoint(client):
    response = client.get("/api/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
