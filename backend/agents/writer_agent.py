"""
Writer Agent

Responsible for generating the final user-facing report.
"""

from backend.core.agent import BaseAgent
from backend.core.state import WorkflowState

NO_VERIFICATION_CONTEXT = (
    "No verification was requested. Generate the report directly from the research."
)


class WriterAgent(BaseAgent):
    """
    AI agent responsible for generating the final report.
    """

    prompt_file = "writer.md"

    def __init__(self, llm):
        super().__init__(
            llm=llm,
            name="Writer Agent",
            role="Report Writer",
        )

    def execute(self, state: WorkflowState) -> WorkflowState:
        """
        Generate the final report.

        Args:
            state: Shared workflow state.

        Returns:
            WorkflowState: State updated with the final report.
        """

        self.require_valid(state)

        if not state.research:
            raise ValueError("Research must be completed before generating a report.")

        verification_context = state.verification or NO_VERIFICATION_CONTEXT

        messages = self.build_messages(
            f"""User Query:

{state.query}

Research Plan:

{state.plan}

Research Output:

{state.research}

Verification Result:

{verification_context}

Instructions:

- If the verification recommends improvements,
  incorporate them before writing the report.

- If the verification says the research is ready,
  generate the report directly.

- If no verification exists,
  generate the report from the research output.

The final report must be concise,
professional,
well-structured,
easy to read,
and suitable for export as Markdown, PDF or DOCX.
"""
        )

        state.set_final_report(self.llm.chat(messages))

        return state
