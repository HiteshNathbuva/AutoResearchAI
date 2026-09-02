"""
Base Agent Module

This module provides the foundational agent structure for all AI agents in the
system. It defines the base class and interface that specialized agents must
implement.

Every agent shares one injected :class:`~backend.core.llm.LLMClient` and follows
a single contract::

    execute(state: WorkflowState) -> WorkflowState

TODO (Phase 1):
- Add lifecycle hooks
- Add callback support
- Add execution metrics
- Add memory integration
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from backend.core.state import WorkflowState
from backend.utils.prompt_loader import load_prompt


class BaseAgent(ABC):
    """
    Base class for all AI agents.

    Every specialized agent should inherit from this class.

    Responsibilities:
    - Store common agent information
    - Hold the shared LLM client
    - Define a common execution interface
    """

    #: Prompt file, relative to the ``prompts/`` directory, used by this agent.
    prompt_file: str = ""

    def __init__(self, llm: Any, name: str, role: str):
        """
        Initialize the base agent.

        Args:
            llm: Shared LLM client used for completions.
            name: Human-readable agent name.
            role: Agent responsibility.
        """

        if llm is None:
            raise ValueError("An LLM client is required.")

        self.llm = llm
        self.name = name
        self.role = role

    @abstractmethod
    def execute(self, state: WorkflowState) -> WorkflowState:
        """
        Execute the agent's primary task.

        Every child agent MUST implement this method, accept the shared
        workflow state, and return the updated state.

        Args:
            state: Shared workflow state.

        Returns:
            WorkflowState: The updated workflow state.
        """
        raise NotImplementedError(
            "Child agents must implement the execute() method."
        )

    def validate(self, state: Any) -> bool:
        """
        Validate the workflow state before execution.

        Args:
            state: Candidate workflow state.

        Returns:
            bool: True when the state carries a usable query.
        """

        if state is None:
            return False

        query = getattr(state, "query", None)

        return bool(query and str(query).strip())

    def system_prompt(self) -> str:
        """Load this agent's system prompt."""

        if not self.prompt_file:
            raise ValueError(f"{self.name} does not define a prompt file.")

        return load_prompt(self.prompt_file)

    def build_messages(self, user_content: str) -> List[Dict[str, str]]:
        """Build a standard system/user message pair."""

        return [
            {"role": "system", "content": self.system_prompt()},
            {"role": "user", "content": user_content},
        ]

    def require_valid(self, state: Any) -> WorkflowState:
        """Validate ``state`` or raise ``ValueError``."""

        if not self.validate(state):
            raise ValueError("Workflow state must contain a non-empty query.")

        return state

    def cleanup(self):
        """
        Cleanup resources after execution.

        Reserved for future enhancements.
        """

        return None
