"""
Writer Agent

Responsible for generating the final user-facing report.
"""

from backend.core.agent import BaseAgent
from backend.utils.prompt_loader import load_prompt


class WriterAgent(BaseAgent):
    """
    AI agent responsible for generating the final report.
    """

    def __init__(self):
        super().__init__(
            name="Writer Agent",
            role="Report Writer"
        )

    def execute(self, state):
        """
        Generate the final report.

        Args:
            state:
                Shared workflow state.

        Returns:
            Updated workflow state.
        """

        if not self.validate(state):
            raise ValueError("Workflow state cannot be empty.")

        system_prompt = load_prompt("writer.md")

        verification_context = (
            state.verification
            if state.verification
            else "No verification was requested. Generate the report directly from the research."
        )

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": f"""
User Query:

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
            },
        ]

        state.set_final_report(self.llm.chat(messages))

        return state
