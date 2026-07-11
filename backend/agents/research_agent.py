"""
Research Agent

Responsible for answering research queries using the configured LLM.
"""

from backend.core.agent import BaseAgent


class ResearchAgent(BaseAgent):
    """
    AI agent responsible for performing research tasks.
    """

    def __init__(self):
        super().__init__(
            name="Research Agent",
            role="Research Specialist"
        )

    def execute(self, input_data):
        """
        Execute a research request.

        Args:
            input_data (str): Research question.

        Returns:
            str: LLM response.
        """

        if not self.validate(input_data):
            raise ValueError("Input data cannot be empty.")

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert AI research assistant. "
                    "Provide accurate, clear and well-structured answers."
                )
            },
            {
                "role": "user",
                "content": input_data
            }
        ]

        return self.llm.chat(messages)