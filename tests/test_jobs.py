"""Background job runner and the asynchronous job API.

Every test is offline. The default :class:`FakeLLMClient` is fast enough that
jobs complete almost immediately; a blocking fake LLM is used where a test must
observe an in-flight job (liveness and the duplicate-job guard).
"""

import tempfile
import threading
import time

import pytest
from fastapi.testclient import TestClient

from backend.core.config import Settings
from backend.core.container import build_resources
from backend.core.exceptions import LLMError
from backend.core.jobs import JobConflictError
from backend.core.state import WorkflowState
from backend.core.statuses import FAILED, is_terminal_status
from backend.main import create_app


def _poll(client, session_id, timeout: float = 5.0):
    deadline = time.time() + timeout
    body = {}
    while time.time() < deadline:
        body = client.get(f"/api/jobs/{session_id}").json()
        if is_terminal_status(body["status"]) and not body["job_active"]:
            return body
        time.sleep(0.02)
    return body


def test_research_job_is_accepted_and_reaches_terminal(client):
    response = client.post("/api/jobs/research", json={"query": "explain vector databases"})

    assert response.status_code == 202
    accepted = response.json()
    assert accepted["session_id"]
    assert accepted["job_active"] is True
    assert accepted["poll_url"].endswith(accepted["session_id"])

    # The session row exists immediately, before the workflow finishes.
    assert client.get(f"/api/sessions/{accepted['session_id']}").status_code == 200

    final = _poll(client, accepted["session_id"])
    assert final["status"] == "Research completed"
    assert final["job_active"] is False
    assert final["completed_tasks"] == ["Planner", "Research"]
    assert final["research"]
    assert final["error"] == ""


def test_research_job_persists_progress_and_survives_reload(client):
    accepted = client.post("/api/jobs/research", json={"query": "what is retrieval augmented generation?"}).json()
    session_id = accepted["session_id"]
    final = _poll(client, session_id)
    assert final["status"] == "Research completed"

    # A fresh read from SQLite (simulating a restart) returns the same content.
    reloaded = client.get(f"/api/sessions/{session_id}").json()
    assert reloaded["research"] == final["research"]
    assert reloaded["plan"] == final["plan"]
    assert reloaded["status"] == "Research completed"


def test_failed_research_job_is_persisted_with_a_safe_error(client, fake_llm):
    fake_llm.error = LLMError("provider down")

    accepted = client.post("/api/jobs/research", json={"query": "a question that will fail"}).json()
    final = _poll(client, accepted["session_id"])

    assert final["status"] == FAILED
    assert final["job_active"] is False
    assert final["error"]
    assert "provider down" in final["error"]
    # The failed run remains diagnosable in history rather than vanishing.
    ids = [row["session_id"] for row in client.get("/api/sessions").json()["sessions"]]
    assert accepted["session_id"] in ids


def test_verify_and_report_jobs_complete(client):
    session_id = client.post("/api/jobs/research", json={"query": "explain embeddings"}).json()["session_id"]
    assert _poll(client, session_id)["status"] == "Research completed"

    verify = client.post(f"/api/jobs/verify/{session_id}")
    assert verify.status_code == 202
    verified = _poll(client, session_id)
    assert verified["status"] == "Verified report generated"
    assert verified["confidence"] == "High"
    assert verified["report"]

    report = client.post(f"/api/jobs/report/{session_id}")
    assert report.status_code == 202
    reported = _poll(client, session_id)
    assert reported["status"] in {"Report generated", "Verified report generated"}
    assert reported["report"]


def test_job_endpoints_reject_unknown_session(client):
    assert client.post("/api/jobs/verify/missing").status_code == 404
    assert client.post("/api/jobs/report/missing").status_code == 404
    assert client.get("/api/jobs/missing").status_code == 404


def test_research_job_validates_the_query(client):
    assert client.post("/api/jobs/research", json={"query": "ab"}).status_code == 422


def test_duplicate_job_for_an_active_session_is_rejected():
    """A second job against a running session must return 409, not corrupt state."""

    class BlockingLLM:
        def __init__(self):
            self.entered = threading.Event()
            self.release = threading.Event()
            self.model = "blocking"
            self.calls = []

        def chat(self, messages, model=None):
            self.calls.append(messages)
            self.entered.set()
            self.release.wait(timeout=5)
            return "# Plan\n\nobjective"

    tmp = tempfile.mkdtemp()
    settings = Settings(OPENROUTER_API_KEY="test-key", ENVIRONMENT="test", LOG_LEVEL="WARNING",
                        DATABASE_PATH=f"{tmp}/blocking.sqlite3", _env_file=None)
    resources = build_resources(settings=settings, llm_client=BlockingLLM())
    app = create_app(settings=settings, resources=resources)
    with TestClient(app) as client:
        session_id = client.post("/api/jobs/research", json={"query": "blocking topic"}).json()["session_id"]
        resources.llm_client.entered.wait(timeout=5)

        job = client.get(f"/api/jobs/{session_id}").json()
        assert job["job_active"] is True

        conflict = client.post(f"/api/jobs/verify/{session_id}")
        assert conflict.status_code == 409
        assert "already running" in conflict.json()["detail"]

        resources.llm_client.release.set()
        final = _poll(client, session_id)
        assert final["status"] == "Research completed"


def test_job_runner_raises_conflict_for_active_session(resources):
    runner = resources.job_runner
    state = WorkflowState()
    state.update_query("a real persisted question")
    session_id = resources.session_manager.create_session(state)

    runner._active.add(session_id)  # noqa: SLF001 - simulate an in-flight job
    try:
        with pytest.raises(JobConflictError):
            runner.start_verify(session_id)
        with pytest.raises(JobConflictError):
            runner.start_report(session_id)
    finally:
        runner._active.discard(session_id)  # noqa: SLF001


def test_ready_endpoint_reports_database_ok(client):
    response = client.get("/api/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready", "database": "ok"}


def test_health_endpoint_remains_static(client):
    # The liveness probe contract must stay stable for existing clients.
    assert client.get("/api/health").json() == {"status": "healthy"}


def test_failed_verify_job_records_error(client, fake_llm):
    session_id = client.post("/api/jobs/research", json={"query": "topic for verify failure"}).json()["session_id"]
    _poll(client, session_id)

    fake_llm.error = LLMError("verifier unavailable")
    client.post(f"/api/jobs/verify/{session_id}")
    final = _poll(client, session_id)

    assert final["status"] == FAILED
    assert "verifier unavailable" in final["error"]
    # Earlier, successfully researched content is preserved.
    assert final["research"]
