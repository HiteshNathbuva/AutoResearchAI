"""Workflow orchestration and confidence parsing."""

import pytest

from backend.core.state import WorkflowState
from backend.core.workflow import WorkflowOrchestrator

parse_confidence = WorkflowOrchestrator._confidence_from_verification


def test_execute_pipeline_runs_planner_then_research(workflow, fake_llm):
    state = workflow.execute_pipeline("explain ai agents")

    assert isinstance(state, WorkflowState)
    assert state.query == "explain ai agents"
    assert state.plan
    assert state.research
    assert state.completed_tasks == ["Planner", "Research"]
    assert state.status == "Research completed"
    assert state.confidence == "Unverified"
    assert state.reading_time >= 1
    assert fake_llm.call_count == 2


def test_execute_pipeline_does_not_write_a_report(workflow):
    state = workflow.execute_pipeline("explain ai agents")
    assert state.final_report == ""
    assert state.verification == ""


def test_execute_pipeline_rejects_empty_query(workflow):
    with pytest.raises(ValueError):
        workflow.execute_pipeline("   ")


def test_verify_report_runs_verifier_then_writer(workflow, fake_llm, researched_state):
    state = workflow.verify_report(researched_state)

    assert state.verification
    assert state.final_report
    assert state.completed_tasks == ["Planner", "Research", "Verification", "Writer"]
    assert state.status == "Verified report generated"
    assert state.confidence == "High"
    assert fake_llm.call_count == 2


def test_verify_report_requires_research(workflow):
    state = WorkflowState()
    state.update_query("topic")
    with pytest.raises(ValueError, match="Research must be completed"):
        workflow.verify_report(state)


def test_generate_report_runs_writer_only(workflow, fake_llm, researched_state):
    state = workflow.generate_report(researched_state)

    assert state.final_report
    assert state.verification == ""
    assert state.status == "Report generated"
    assert "Writer" in state.completed_tasks
    assert fake_llm.call_count == 1


def test_generate_report_requires_research(workflow):
    state = WorkflowState()
    state.update_query("topic")
    with pytest.raises(ValueError, match="Research must be completed"):
        workflow.generate_report(state)


def test_reading_time_is_derived_from_word_count(workflow, researched_state):
    state = workflow.generate_report(researched_state)
    expected = max(1, round(len(state.final_report.split()) / 200))
    assert state.reading_time == expected


def test_all_agents_share_one_llm(workflow, fake_llm):
    assert workflow.planner_agent.llm is fake_llm
    assert workflow.research_agent.llm is fake_llm
    assert workflow.verifier_agent.llm is fake_llm
    assert workflow.writer_agent.llm is fake_llm


@pytest.mark.parametrize("text,expected", [
    ("Confidence: High", "High"),
    ("confidence: medium", "Medium"),
    ("Confidence: low", "Low"),
    ("**Confidence:** High", "High"),
    ("Confidence: **High**", "High"),
    ("Confidence:  High", "High"),
    ("Confidence - Low", "Low"),
    ("Confidence:\tMedium", "Medium"),
    ("Confidence *High*", "High"),
    ("Overall Score: 9/10\nConfidence: High\n\n## Summary", "High"),
    ("# AI Fact Check\n\n**Confidence:**  **Medium**\n", "Medium"),
])
def test_confidence_parsing_tolerates_markdown_and_spacing(text, expected):
    """Regression tests for the brittle substring parser."""

    assert parse_confidence(text) == expected


@pytest.mark.parametrize("text", ["", None, "no confidence marker here",
                                  "Confidence: unknown", "Score: 8/10"])
def test_confidence_defaults_to_unverified(text):
    assert parse_confidence(text) == "Unverified"


def test_confidence_flows_from_verification_text(fake_llm, researched_state):
    from backend.core.container import build_workflow

    fake_llm.responses = {"Fact Check Agent": "Overall Score: 5/10\n\n**Confidence:** Low\n"}
    state = build_workflow(fake_llm).verify_report(researched_state)

    assert state.confidence == "Low"
