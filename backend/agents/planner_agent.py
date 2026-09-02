"""
Planner Agent

Responsible for breaking complex research queries into
a structured research plan.
"""

from backend.core.agent import BaseAgent
from backend.core.state import WorkflowState


class PlannerAgent(BaseAgent):
    """
    AI agent responsible for planning research tasks.
    """

    prompt_file = "planner.md"

    def __init__(self, llm):
        super().__init__(
            llm=llm,
            name="Planner Agent",
            role="Research Planner",
        )

    def execute(self, state: WorkflowState) -> WorkflowState:
        """
        Generate a research plan.

        Args:
            state: Shared workflow state carrying the user query.

        Returns:
            WorkflowState: State updated with the structured research plan.
        """

        self.require_valid(state)

        messages = self.build_messages(state.query)

        state.update_plan(self.llm.chat(messages))

        return state
