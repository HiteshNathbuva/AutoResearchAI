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

Research Notes:

{state.research}

Verification Report:

{state.verification}
"""
            },
        ]

        state.final_report = self.llm.chat(messages)

        state.mark_task_complete("Writer")

        return state