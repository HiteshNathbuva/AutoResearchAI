"""
Verifier Agent

Responsible for reviewing and validating research produced by
the Research Agent.

The Verifier DOES NOT rewrite the research.
Its responsibility is to identify strengths, weaknesses,
missing information, and overall research quality.
"""

from backend.core.agent import BaseAgent
from backend.core.state import WorkflowState


class VerifierAgent(BaseAgent):
    """
    AI agent responsible for verifying research quality.
    """

    prompt_file = "verifier.md"

    def __init__(self, llm):
        super().__init__(
            llm=llm,
            name="Verifier Agent",
            role="Research Verifier",
        )

    def execute(self, state: WorkflowState) -> WorkflowState:
        """
        Verify research output.

        Args:
            state: Shared workflow state carrying the research output.

        Returns:
            WorkflowState: State updated with the verification report.
        """

        self.require_valid(state)

        if not state.research:
            raise ValueError("Research must be completed before verification.")

        messages = self.build_messages(
            f"""User Query:

{state.query}

Research Plan:

{state.plan}

Research Output:

{state.research}
"""
        )

        state.update_verification(self.llm.chat(messages))

        return state
