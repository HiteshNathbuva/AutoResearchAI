"""
Planner Agent

Responsible for breaking complex research queries into
a structured research plan.
"""

from backend.core.agent import BaseAgent
from backend.utils.prompt_loader import load_prompt


class PlannerAgent(BaseAgent):
    """
    AI agent responsible for planning research tasks.
    """

    def __init__(self):
        super().__init__(
            name="Planner Agent",
            role="Research Planner"
        )

    def execute(self, input_data):
        """
        Generate a research plan.

        Args:
            input_data (str): User research query.

        Returns:
            str: Structured research plan.
        """

        if not self.validate(input_data):
            raise ValueError("Input data cannot be empty.")

        system_prompt = load_prompt("planner.md")

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": input_data,
            },
        ]

        return self.llm.chat(messages)