"""
Research Agent

Responsible for answering research queries using the configured LLM.
"""

from backend.core.agent import BaseAgent
from backend.utils.prompt_loader import load_prompt


class ResearchAgent(BaseAgent):
    """
    AI agent responsible for performing research tasks.
    """

    def __init__(self):
        super().__init__(
            name="Research Agent",
            role="Research Specialist"
        )

    def execute(self, state):
        """
        Execute a research request.

        Args:
            input_data (str): Research question.

        Returns:
            str: LLM response.
        """

        if not self.validate(state):
            raise ValueError("Input data cannot be empty.")

        system_prompt = load_prompt("researcher.md")

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
            """
            }
        ]

        state.research = self.llm.chat(messages)

        return state