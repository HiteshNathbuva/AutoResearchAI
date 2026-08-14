"""
Verifier Agent

Responsible for reviewing and validating research produced by
the Research Agent.

The Verifier DOES NOT rewrite the research.
Its responsibility is to identify strengths, weaknesses,
missing information, and overall research quality.
"""

from backend.core.agent import BaseAgent
from backend.utils.prompt_loader import load_prompt


class VerifierAgent(BaseAgent):
    """
    AI agent responsible for verifying research quality.
    """

    def __init__(self):
        super().__init__(
            name="Verifier Agent",
            role="Research Verifier"
        )

    def execute(self, state):
        """
        Verify research output.

        Args:
            input_data (str):
                Research content to verify.

        Returns:
            str:
                Verification report.
        """

        if not self.validate(state):
            raise ValueError("Input data cannot be empty.")

        system_prompt = load_prompt("verifier.md")

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": state.research,
                }
        ]

        state.update_verification(self.llm.chat(messages))

        return state
