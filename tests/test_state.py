"""WorkflowState behaviour and serialization round-trip."""

import pytest

from backend.core.state import WorkflowState


def test_initial_state_defaults():
    state = WorkflowState()
    assert state.query == ""
    assert state.status == "Initialized"
    assert state.confidence == "Unverified"
    assert state.reading_time == 0
    assert state.completed_tasks == []
    assert state.current_step == "Initialized"
    assert state.memory == {}


def test_update_query_strips_whitespace():
    state = WorkflowState()
    state.update_query("  quantum computing  ")
    assert state.query == "quantum computing"
    assert state.user_query == "quantum computing"


@pytest.mark.parametrize("bad_query", ["", "   ", None])
def test_update_query_rejects_empty(bad_query):
    state = WorkflowState()
    with pytest.raises(ValueError):
        state.update_query(bad_query)


def test_research_alias_tracks_research():
    state = WorkflowState()
    state.add_research_note("findings")
    assert state.research == "findings"
    assert state.research_notes == "findings"


def test_reading_time_has_minimum_of_one():
    state = WorkflowState()
    state.set_reading_time(0)
    assert state.reading_time == 1


def test_mark_task_complete_is_idempotent():
    state = WorkflowState()
    state.mark_task_complete("Planner")
    state.mark_task_complete("Planner")
    state.mark_task_complete("Research")
    assert state.completed_tasks == ["Planner", "Research"]
    assert state.current_step == "Research"


def test_timestamps_advance_on_mutation():
    state = WorkflowState()
    original = state.metadata["updated_at"]
    state.update_status("Planning")
    assert state.metadata["updated_at"] >= original


def test_round_trip_preserves_all_serialized_fields():
    state = WorkflowState()
    state.update_query("multi agent systems")
    state.update_plan("the plan")
    state.add_research_note("the research")
    state.update_verification("Confidence: High")
    state.set_final_report("the report")
    state.update_status("Report generated")
    state.set_confidence("High")
    state.set_reading_time(4)
    state.mark_task_complete("Planner")
    state.mark_task_complete("Writer")

    restored = WorkflowState.from_dict(state.to_dict())

    assert restored.to_dict() == state.to_dict()
    assert restored.query == "multi agent systems"
    assert restored.plan == "the plan"
    assert restored.research == "the research"
    assert restored.verification == "Confidence: High"
    assert restored.final_report == "the report"
    assert restored.status == "Report generated"
    assert restored.confidence == "High"
    assert restored.reading_time == 4
    assert restored.completed_tasks == ["Planner", "Writer"]
    assert restored.current_step == "Writer"


def test_from_dict_tolerates_missing_and_null_values():
    state = WorkflowState.from_dict({"query": "topic"})
    assert state.query == "topic"
    assert state.plan == ""
    assert state.confidence == "Unverified"
    assert state.reading_time == 0
    assert state.completed_tasks == []

    nulled = WorkflowState.from_dict({"query": "topic", "confidence": None,
                                      "reading_time": None, "completed_tasks": None,
                                      "plan": None})
    assert nulled.confidence == "Unverified"
    assert nulled.reading_time == 0
    assert nulled.completed_tasks == []
    assert nulled.plan == ""


def test_to_dict_returns_a_copy_of_completed_tasks():
    state = WorkflowState()
    state.mark_task_complete("Planner")
    data = state.to_dict()
    data["completed_tasks"].append("Mutated")
    assert state.completed_tasks == ["Planner"]
