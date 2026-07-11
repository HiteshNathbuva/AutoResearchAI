"""
Base Agent Module

This module provides the foundational agent structure for all AI agents in the system.
It defines the base class and interface that specialized agents must implement.

TODO:
- Add lifecycle hooks
- Add callback support
- Add execution metrics
- Add memory integration
"""

from abc import ABC, abstractmethod

from backend.core.llm import LLMClient


class BaseAgent(ABC):
    """
    Base class for all AI agents.

    Every specialized agent should inherit from this class.

    Responsibilities:
    - Store common agent information
    - Provide access to the shared LLM client
    - Define a common execution interface
    """

    def __init__(self, name: str, role: str):
        """
        Initialize the base agent.

        Args:
            name: Human-readable agent name.
            role: Agent responsibility.
        """

        self.name = name
        self.role = role
        self.llm = LLMClient()

    @abstractmethod
    def execute(self, input_data):
        """
        Execute the agent's primary task.

        Every child agent MUST implement this method.

        Args:
            input_data:
                Input required for execution.

        Returns:
            Agent output.
        """
        raise NotImplementedError(
            "Child agents must implement the execute() method."
        )

    def validate(self, input_data):
        """
        Validate input before execution.

        Args:
            input_data:
                Input data.

        Returns:
            bool
        """

        if input_data is None:
            return False

        return True

    def cleanup(self):
        """
        Cleanup resources after execution.

        Reserved for future enhancements.
        """

        return None