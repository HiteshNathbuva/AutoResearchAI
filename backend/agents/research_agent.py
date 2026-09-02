"""
Research Agent

Responsible for answering research queries using the configured LLM.
"""

from backend.core.agent import BaseAgent
from backend.core.state import WorkflowState


class ResearchAgent(BaseAgent):
    """
    AI agent responsible for performing research tasks.
    """

    prompt_file = "researcher.md"

    def __init__(self, llm):
        super().__init__(
            llm=llm,
            name="Research Agent",
            role="Research Specialist",
        )

    def execute(self, state: WorkflowState) -> WorkflowState:
        """
        Execute a research request.

        Args:
            state: Shared workflow state carrying the query and research plan.

        Returns:
            WorkflowState: State updated with the research output.
        """

        self.require_valid(state)

        messages = self.build_messages(
            f"""User Query:

{state.query}

Research Plan:

{state.plan}
"""
        )

        state.add_research_note(self.llm.chat(messages))

        return state
