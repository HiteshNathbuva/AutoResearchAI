"""Agent execution contract: every agent takes and returns WorkflowState."""

import pytest

from backend.agents.planner_agent import PlannerAgent
from backend.agents.research_agent import ResearchAgent
from backend.agents.verifier_agent import VerifierAgent
from backend.agents.writer_agent import WriterAgent
from backend.core.agent import BaseAgent
from backend.core.state import WorkflowState

AGENT_CLASSES = [PlannerAgent, ResearchAgent, VerifierAgent, WriterAgent]


def _ready_state() -> WorkflowState:
    state = WorkflowState()
    state.update_query("what is a vector database")
    state.update_plan("a plan")
    state.add_research_note("some research")
    return state


@pytest.mark.parametrize("agent_class", AGENT_CLASSES)
def test_all_agents_subclass_base_agent(agent_class):
    assert issubclass(agent_class, BaseAgent)


@pytest.mark.parametrize("agent_class", AGENT_CLASSES)
def test_all_agents_declare_a_prompt_file(agent_class, fake_llm):
    agent = agent_class(fake_llm)
    assert agent.prompt_file
    assert agent.system_prompt()


@pytest.mark.parametrize("agent_class", AGENT_CLASSES)
def test_every_agent_accepts_and_returns_state(agent_class, fake_llm):
    """The standardized contract: execute(state) -> state."""

    agent = agent_class(fake_llm)
    state = _ready_state()

    result = agent.execute(state)

    assert isinstance(result, WorkflowState)
    assert result is state
    assert fake_llm.call_count == 1


@pytest.mark.parametrize("agent_class", AGENT_CLASSES)
def test_agents_share_the_injected_llm(agent_class, fake_llm):
    agent = agent_class(fake_llm)
    assert agent.llm is fake_llm


@pytest.mark.parametrize("agent_class", AGENT_CLASSES)
def test_agents_require_an_llm(agent_class):
    with pytest.raises(ValueError):
        agent_class(None)


@pytest.mark.parametrize("agent_class", AGENT_CLASSES)
def test_agents_reject_none_state(agent_class, fake_llm):
    with pytest.raises(ValueError):
        agent_class(fake_llm).execute(None)


@pytest.mark.parametrize("agent_class", AGENT_CLASSES)
def test_agents_reject_empty_query(agent_class, fake_llm):
    with pytest.raises(ValueError):
        agent_class(fake_llm).execute(WorkflowState())
    assert fake_llm.call_count == 0


def test_planner_writes_the_plan(fake_llm):
    state = WorkflowState()
    state.update_query("topic")

    result = PlannerAgent(fake_llm).execute(state)

    assert result.plan
    assert "Research Plan" in result.plan


def test_research_agent_receives_query_and_plan(fake_llm):
    state = WorkflowState()
    state.update_query("distributed tracing")
    state.update_plan("PLAN-MARKER")

    result = ResearchAgent(fake_llm).execute(state)

    user_message = fake_llm.calls[0]["messages"][1]["content"]
    assert "distributed tracing" in user_message
    assert "PLAN-MARKER" in user_message
    assert result.research


def test_verifier_requires_research(fake_llm):
    state = WorkflowState()
    state.update_query("topic")

    with pytest.raises(ValueError, match="Research must be completed"):
        VerifierAgent(fake_llm).execute(state)


def test_verifier_sees_query_plan_and_research(fake_llm):
    state = _ready_state()
    state.update_plan("PLAN-MARKER")
    state.add_research_note("RESEARCH-MARKER")

    result = VerifierAgent(fake_llm).execute(state)

    user_message = fake_llm.calls[0]["messages"][1]["content"]
    assert "PLAN-MARKER" in user_message
    assert "RESEARCH-MARKER" in user_message
    assert result.verification


def test_writer_requires_research(fake_llm):
    state = WorkflowState()
    state.update_query("topic")

    with pytest.raises(ValueError, match="Research must be completed"):
        WriterAgent(fake_llm).execute(state)


def test_writer_notes_absent_verification(fake_llm):
    result = WriterAgent(fake_llm).execute(_ready_state())

    user_message = fake_llm.calls[0]["messages"][1]["content"]
    assert "No verification was requested" in user_message
    assert result.final_report


def test_writer_includes_verification_when_present(fake_llm):
    state = _ready_state()
    state.update_verification("VERIFICATION-MARKER")

    WriterAgent(fake_llm).execute(state)

    user_message = fake_llm.calls[0]["messages"][1]["content"]
    assert "VERIFICATION-MARKER" in user_message
    assert "No verification was requested" not in user_message


def test_messages_are_system_then_user(fake_llm):
    PlannerAgent(fake_llm).execute(_ready_state())
    messages = fake_llm.calls[0]["messages"]
    assert [message["role"] for message in messages] == ["system", "user"]


def test_base_agent_cannot_be_instantiated(fake_llm):
    with pytest.raises(TypeError):
        BaseAgent(fake_llm, "name", "role")


def test_agent_without_prompt_file_raises(fake_llm):
    class PromptlessAgent(BaseAgent):
        def execute(self, state):
            return state

    with pytest.raises(ValueError):
        PromptlessAgent(fake_llm, "Promptless", "None").system_prompt()
