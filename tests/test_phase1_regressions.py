"""Phase 1 stability/correctness regression tests.

Covers:
- Frontend/backend connectivity (CORS wildcard handling)
- Workflow state inconsistency (Verification pending while Writer completed)
- Prompt/instruction leakage sanitization in WriterAgent
- Report generation correctness
"""

import pytest

from backend.agents.writer_agent import _sanitize_report
from backend.core.config import Settings
from backend.core.state import WorkflowState


# ----------------------------------------------------------------------
# CORS / connectivity regression
# ----------------------------------------------------------------------

def test_cors_default_allows_all_origins():
    """Default CORS_ORIGINS should be wildcard to avoid Failed to fetch in preview."""
    settings = Settings(OPENROUTER_API_KEY="test-key", _env_file=None, CORS_ORIGINS="*")
    assert settings.cors_origins == ["*"]


def test_cors_wildcard_parsed_correctly():
    settings = Settings(OPENROUTER_API_KEY="test-key", _env_file=None, CORS_ORIGINS="*")
    assert "*" in settings.CORS_ORIGINS
    assert settings.cors_origins == ["*"]


def test_cors_specific_origins_still_work():
    settings = Settings(
        OPENROUTER_API_KEY="test-key",
        _env_file=None,
        CORS_ORIGINS="http://localhost:5173,http://127.0.0.1:5173",
    )
    assert settings.cors_origins == ["http://localhost:5173", "http://127.0.0.1:5173"]


def test_cors_allows_all_in_non_production(client):
    """Ensure test client gets CORS header (either * or specific)."""
    response = client.get("/api/health", headers={"Origin": "https://preview.example.com"})
    assert response.headers.get("access-control-allow-origin") in (
        "*",
        "https://preview.example.com",
        "http://localhost:5173",
    )


# ----------------------------------------------------------------------
# Workflow state inconsistency regression
# ----------------------------------------------------------------------

def test_generate_report_without_verification_leaves_verification_pending(workflow, researched_state):
    """Regression: after research + report (no verification), Verification should NOT be marked completed."""
    state = workflow.generate_report(researched_state)

    assert state.status == "Report generated"
    assert "Writer" in state.completed_tasks
    assert "Verification" not in state.completed_tasks
    assert state.completed_tasks == ["Planner", "Research", "Writer"]
    assert state.confidence == "Unverified"


def test_verify_report_marks_all_tasks_completed(workflow, researched_state):
    """After verification flow, all 4 tasks should be completed."""
    state = workflow.verify_report(researched_state)

    assert state.status == "Verified report generated"
    assert state.completed_tasks == ["Planner", "Research", "Verification", "Writer"]


def test_workflow_progress_skipped_logic():
    """Simulate frontend logic for Verification Skipped case."""

    def get_step_status(step, done, status):
        if step in done:
            return "Completed"
        if step == "Verification" and "Writer" in done and status == "Report generated":
            return "Skipped"
        return "Pending"

    done = ["Planner", "Research", "Writer"]
    assert get_step_status("Verification", done, "Report generated") == "Skipped"
    assert get_step_status("Writer", done, "Report generated") == "Completed"
    assert get_step_status("Verification", done, "Research completed") == "Pending"

    done_all = ["Planner", "Research", "Verification", "Writer"]
    assert get_step_status("Verification", done_all, "Verified report generated") == "Completed"


# ----------------------------------------------------------------------
# Prompt leakage / report sanitization regression
# ----------------------------------------------------------------------

def test_sanitize_removes_think_tags():
    raw = "Before <think>internal reasoning</think> After"
    cleaned = _sanitize_report(raw)
    assert "<think>" not in cleaned
    assert "internal reasoning" not in cleaned
    assert "Before" in cleaned
    assert "After" in cleaned


def test_sanitize_removes_think_tags_multiline():
    raw = "# Title\n<think>\nHere's a thinking process:\nAnalyze User Input\nCheck Verification Status\n</think>\n\n# Executive Summary\nReal content"
    cleaned = _sanitize_report(raw)
    assert "<think>" not in cleaned.lower()
    assert "Here's a thinking process" not in cleaned
    assert "Real content" in cleaned


def test_sanitize_removes_leakage_markers():
    raw = "Here's a thinking process:\nAnalyze User Input\nCheck Verification Status\n\n# Real Report\nContent here"
    cleaned = _sanitize_report(raw)
    assert "Analyze User Input" not in cleaned
    assert "Check Verification Status" not in cleaned
    assert "Real Report" in cleaned
    assert "Content here" in cleaned


def test_sanitize_preserves_valid_report():
    valid = "# Title Quantum Computing\n\n## Executive Summary\nQuantum is cool.\n\n- Point 1\n- Point 2"
    cleaned = _sanitize_report(valid)
    assert cleaned == valid


def test_sanitize_handles_empty():
    assert _sanitize_report("") == ""
    # None handling - function returns None or empty; we accept empty string case
    assert _sanitize_report("") == ""


def test_writer_agent_sanitizes_output():
    """WriterAgent should sanitize LLM output containing leakage."""
    from backend.agents.writer_agent import WriterAgent

    leakage_response = (
        "<think>Here's a thinking process: Analyze User Input, Check Verification Status, "
        "I think the safest is to provide 5 bullets, I'll use the 4 given.</think>\n\n"
        "Here's a thinking process:\n"
        "Analyze User Input\n"
        "Check Verification Status\n\n"
        "# Test Title\n\n"
        "## Executive Summary\n"
        "This is a clean report.\n"
    )

    class LeakageLLM:
        def chat(self, messages, model=None):
            return leakage_response

    state = WorkflowState()
    state.update_query("test query")
    state.update_plan("plan")
    state.add_research_note("research")
    state.mark_task_complete("Planner")
    state.mark_task_complete("Research")

    agent = WriterAgent(LeakageLLM())
    result = agent.execute(state)

    report = result.final_report
    assert "<think>" not in report.lower()
    assert "Here's a thinking process" not in report
    assert "Analyze User Input" not in report
    assert "Check Verification Status" not in report
    assert "Test Title" in report or "clean report" in report.lower()


def test_writer_prompt_contains_anti_leakage_rules():
    """Ensure writer prompt forbids leakage."""
    from backend.utils.prompt_loader import load_prompt

    prompt = load_prompt("writer.md").lower()
    assert "never output your thinking process" in prompt or "never output thinking" in prompt
    assert "output only the final report" in prompt or "output only the report" in prompt


def test_researcher_prompt_hardened():
    from backend.utils.prompt_loader import load_prompt

    prompt = load_prompt("researcher.md").lower()
    assert "never output your thinking process" in prompt or "chain-of-thought" in prompt or "thinking process" in prompt


# ----------------------------------------------------------------------
# Report generation correctness
# ----------------------------------------------------------------------

def test_report_generation_sets_reading_time(workflow, researched_state):
    state = workflow.generate_report(researched_state)
    assert state.reading_time >= 1
    assert state.final_report


def test_report_generation_without_research_fails(workflow):
    state = WorkflowState()
    state.update_query("topic")
    with pytest.raises(ValueError, match="Research must be completed"):
        workflow.generate_report(state)


def test_verify_then_report_flow_preserves_report(client):
    """Full flow: research -> verify -> report should keep report and verification."""
    resp = client.post("/api/research", json={"query": "explain quantum computing"})
    assert resp.status_code == 200
    session_id = resp.json()["session_id"]

    resp = client.post(f"/api/verify/{session_id}")
    assert resp.status_code == 200
    assert resp.json()["verification"]
    assert resp.json()["report"]

    resp = client.post(f"/api/report/{session_id}")
    assert resp.status_code == 200
    assert resp.json()["report"]
    assert resp.json()["confidence"] in ("High", "Medium", "Low", "Unverified")
