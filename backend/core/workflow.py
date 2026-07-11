"""
Workflow Orchestrator Module

This module manages the execution of multi-agent research workflows.
It coordinates the interaction between different agents and ensures
proper task sequencing and state management.

Current Pipeline:

User Query
    ↓
Planner
    ↓
Research
    ↓
Verification
    ↓
Future: Writer
"""

from backend.agents.planner_agent import PlannerAgent
from backend.agents.research_agent import ResearchAgent
from backend.agents.verifier_agent import VerifierAgent

from backend.core.state import WorkflowState


class WorkflowOrchestrator:
    """
    Orchestrates the execution of multi-agent research workflows.
    """

    def __init__(self):
        """
        Initialize workflow components.
        """

        self.planner_agent = PlannerAgent()
        self.research_agent = ResearchAgent()
        self.verifier_agent = VerifierAgent()

    def supervisor(self):
        """
        Supervisor Agent

        TODO:
        Implement in future.
        """

        raise NotImplementedError(
            "Supervisor Agent has not been implemented yet."
        )

    def planner(self):
        """
        Planner Agent

        TODO:
        Reserved for future implementation.
        """

        raise NotImplementedError(
            "Planner Agent has not been implemented yet."
        )

    def research(self, state):
        """
        Execute research stage.
        """

        return self.research_agent.execute(state)

    def verification(self, state):
        """
        Execute verification stage.
        """

        return self.verifier_agent.execute(state)

    def writer(self):
        """
        Writer Agent

        TODO:
        Implement in future.
        """

        raise NotImplementedError(
            "Writer Agent has not been implemented yet."
        )

    def execute_pipeline(self, query):
        """
        Execute the complete workflow.
        """

        if not query.strip():
            raise ValueError("Query cannot be empty.")

        state = WorkflowState(query=query)

        # Planner
        state.plan = self.planner_agent.execute(query)
        state.mark_task_complete("Planner")

        # Research
        state = self.research(state)
        state.mark_task_complete("Research")

        # Verification
        state = self.verification(state)
        state.mark_task_complete("Verification")

        return state