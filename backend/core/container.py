"""Composition root for application resources.

Building the object graph in one place keeps wiring out of module import time and
guarantees that a single :class:`~backend.core.llm.LLMClient` is shared by every
agent.
"""

from dataclasses import dataclass
from typing import Any, Optional

from backend.agents.planner_agent import PlannerAgent
from backend.agents.research_agent import ResearchAgent
from backend.agents.verifier_agent import VerifierAgent
from backend.agents.writer_agent import WriterAgent
from backend.core.config import Settings, get_settings
from backend.core.llm import LLMClient
from backend.core.session import SessionManager
from backend.core.workflow import WorkflowOrchestrator


@dataclass
class Resources:
    """Long-lived resources shared across requests."""

    settings: Settings
    llm_client: Any
    session_manager: SessionManager
    workflow: WorkflowOrchestrator


def build_workflow(llm_client: Any) -> WorkflowOrchestrator:
    """Create the orchestrator with all four agents sharing ``llm_client``."""

    return WorkflowOrchestrator(
        planner_agent=PlannerAgent(llm_client),
        research_agent=ResearchAgent(llm_client),
        verifier_agent=VerifierAgent(llm_client),
        writer_agent=WriterAgent(llm_client),
    )


def build_resources(settings: Optional[Settings] = None, llm_client: Optional[Any] = None,
                    session_manager: Optional[SessionManager] = None) -> Resources:
    """Build the full object graph, allowing individual parts to be supplied."""

    settings = settings or get_settings()
    llm_client = llm_client if llm_client is not None else LLMClient(settings=settings)
    session_manager = session_manager or SessionManager(settings.DATABASE_PATH)

    return Resources(settings=settings, llm_client=llm_client,
                     session_manager=session_manager,
                     workflow=build_workflow(llm_client))
