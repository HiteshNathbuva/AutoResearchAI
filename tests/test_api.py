"""API contract tests. All LLM traffic is faked; no network access occurs."""

import pytest

from backend.core.exceptions import LLMError


def _create_session(client) -> str:
    response = client.post("/api/research", json={"query": "explain vector databases"})
    assert response.status_code == 200
    return response.json()["session_id"]


def test_root_returns_application_banner(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["application"] == "AutoResearchAI"
    assert body["status"] == "running"
    assert body["api"] == "/docs"
    assert "version" in body


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_openapi_schema_is_available(client):
    assert client.get("/openapi.json").status_code == 200


def test_research_returns_full_payload(client, fake_llm):
    response = client.post("/api/research", json={"query": "explain vector databases"})

    assert response.status_code == 200
    body = response.json()
    assert body["session_id"]
    assert body["status"] == "Research completed"
    assert body["confidence"] == "Unverified"
    assert body["research"]
    assert body["plan"]
    assert body["report"] == ""
    assert body["verification"] == ""
    assert body["completed_tasks"] == ["Planner", "Research"]
    assert body["reading_time"] >= 1
    assert body["created_at"] and body["updated_at"]
    assert fake_llm.call_count == 2


@pytest.mark.parametrize("payload", [{"query": "ab"}, {"query": ""}, {}, {"query": "x" * 4001}])
def test_research_validates_the_query(client, payload):
    assert client.post("/api/research", json=payload).status_code == 422


def test_research_persists_the_session(client):
    session_id = _create_session(client)
    response = client.get(f"/api/sessions/{session_id}")

    assert response.status_code == 200
    assert response.json()["session_id"] == session_id


def test_research_returns_502_on_llm_failure(client, fake_llm):
    fake_llm.error = LLMError("provider down")

    response = client.post("/api/research", json={"query": "explain vector databases"})

    assert response.status_code == 502
    assert "Research could not be completed" in response.json()["detail"]


def test_list_sessions_is_initially_empty(client):
    response = client.get("/api/sessions")
    assert response.status_code == 200
    assert response.json() == {"sessions": []}


def test_list_sessions_returns_summaries(client):
    session_id = _create_session(client)

    response = client.get("/api/sessions")

    assert response.status_code == 200
    sessions = response.json()["sessions"]
    assert len(sessions) == 1
    summary = sessions[0]
    assert summary["session_id"] == session_id
    assert summary["query"] == "explain vector databases"
    assert summary["has_report"] is False
    assert "research" not in summary


@pytest.mark.parametrize("limit,expected", [(0, 422), (101, 422), (1, 200), (100, 200)])
def test_list_sessions_validates_limit(client, limit, expected):
    assert client.get(f"/api/sessions?limit={limit}").status_code == expected


def test_get_missing_session_returns_404(client):
    response = client.get("/api/sessions/missing-id")
    assert response.status_code == 404
    assert "was not found" in response.json()["detail"]


def test_verify_runs_verifier_and_writer(client, fake_llm):
    session_id = _create_session(client)
    fake_llm.calls.clear()

    response = client.post(f"/api/verify/{session_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["verification"]
    assert body["report"]
    assert body["confidence"] == "High"
    assert body["status"] == "Verified report generated"
    assert body["completed_tasks"] == ["Planner", "Research", "Verification", "Writer"]
    assert fake_llm.call_count == 2


def test_verify_persists_results(client):
    session_id = _create_session(client)
    client.post(f"/api/verify/{session_id}")

    stored = client.get(f"/api/sessions/{session_id}").json()
    assert stored["verification"]
    assert stored["report"]
    assert stored["confidence"] == "High"


def test_verify_missing_session_returns_404(client):
    response = client.post("/api/verify/missing-id")
    assert response.status_code == 404
    assert "was not found" in response.json()["detail"]


def test_verify_returns_502_on_llm_failure(client, fake_llm):
    session_id = _create_session(client)
    fake_llm.error = LLMError("provider down")

    response = client.post(f"/api/verify/{session_id}")

    assert response.status_code == 502
    assert "Verification could not be completed" in response.json()["detail"]


def test_report_runs_writer_only(client, fake_llm):
    session_id = _create_session(client)
    fake_llm.calls.clear()

    response = client.post(f"/api/report/{session_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["report"]
    assert body["verification"] == ""
    assert body["status"] == "Report generated"
    assert fake_llm.call_count == 1


def test_report_persists_and_flags_history(client):
    session_id = _create_session(client)
    client.post(f"/api/report/{session_id}")

    assert client.get(f"/api/sessions/{session_id}").json()["report"]
    assert client.get("/api/sessions").json()["sessions"][0]["has_report"] is True


def test_report_missing_session_returns_404(client):
    response = client.post("/api/report/missing-id")
    assert response.status_code == 404


def test_report_returns_502_on_llm_failure(client, fake_llm):
    session_id = _create_session(client)
    fake_llm.error = LLMError("provider down")

    response = client.post(f"/api/report/{session_id}")

    assert response.status_code == 502
    assert "The report could not be generated" in response.json()["detail"]


def test_full_research_verify_report_flow(client):
    session_id = _create_session(client)
    assert client.post(f"/api/verify/{session_id}").status_code == 200
    assert client.post(f"/api/report/{session_id}").status_code == 200

    final = client.get(f"/api/sessions/{session_id}").json()
    assert final["report"]
    assert final["verification"]


def test_cors_headers_are_exposed(client):
    response = client.get("/api/health", headers={"Origin": "http://localhost:5173"})
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
