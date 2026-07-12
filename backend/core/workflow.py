"""
Workflow Orchestrator Module

This module manages the execution of multi-agent research workflows.
It coordinates the interaction between different agents and ensures
proper task sequencing and state management.

Default Product Flow:

User Query
    ↓
Planner (Hidden)
    ↓
Research
    ↓
Return Research To User

Optional Actions:

AI Fact Check
    ↓
Verification
    ↓
Writer
    ↓
Verified Report

Generate Professional Report
    ↓
Writer
    ↓
PDF / DOCX / Markdown

Future Pipeline:

User Query
    ↓
Supervisor
    ↓
Planner
    ↓
Research
    ↓
Verification
    ↓
Writer
"""

from backend.agents.planner_agent import PlannerAgent
from backend.agents.research_agent import ResearchAgent
from backend.agents.verifier_agent import VerifierAgent
from backend.agents.writer_agent import WriterAgent

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
        self.writer_agent = WriterAgent()

    def supervisor(self):
        raise NotImplementedError(
            "Supervisor Agent has not been implemented yet."
        )

    def planner(self):
        raise NotImplementedError(
            "Planner Agent has not been implemented yet."
        )

    def research(self, state):
        return self.research_agent.execute(state)

    def verification(self, state):
        return self.verifier_agent.execute(state)

    def writer(self, state):
        return self.writer_agent.execute(state)

    # ==========================================================
    # QUICK RESEARCH (Default)
    # ==========================================================

    def execute_pipeline(self, query):
        """
        Execute quick research.

        Planner -> Research

        Returns research immediately.
        """

        if not query.strip():
            raise ValueError("Query cannot be empty.")

        state = WorkflowState(query=query)

        # -------------------------
        # Planning
        # -------------------------

        state.update_status("Planning")

        state.plan = self.planner_agent.execute(query)

        state.mark_task_complete("Planner")

        # -------------------------
        # Research
        # -------------------------

        state.update_status("Researching")

        state = self.research(state)

        state.mark_task_complete("Research")

        # -------------------------
        # Research Finished
        # -------------------------

        state.update_status("Completed")

        state.set_confidence("High")

        state.set_reading_time(3)

        return state

    # ==========================================================
    # OPTIONAL AI FACT CHECK
    # ==========================================================

    def verify_report(self, state):
        """
        Perform deep verification.

        Research
            ↓
        Verification
            ↓
        Writer
        """

        state.update_status("Verifying")

        state = self.verification(state)

        state.mark_task_complete("Verification")

        state.update_status("Writing")

        state = self.writer(state)

        state.mark_task_complete("Writer")

        state.update_status("Verified")

        return state

    # ==========================================================
    # OPTIONAL PROFESSIONAL REPORT
    # ==========================================================

    def generate_report(self, state):
        """
        Generate report directly from research.

        Research
            ↓
        Writer
        """

        state.update_status("Writing")

        state = self.writer(state)

        state.mark_task_complete("Writer")

        state.update_status("Report Generated")

        return state