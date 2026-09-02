"""
Custom Exception Classes Module

This module defines custom exception classes for the application.
These exceptions provide specific error handling for different
components and failure scenarios in the system.
"""


class AgentError(Exception):
    """
    Base exception for agent-related errors.

    Raised when an agent encounters an error during execution,
    validation, or cleanup operations.
    """
    pass


class LLMError(Exception):
    """
    Exception for LLM-related errors.

    Raised when the LLM client encounters errors such as:
    - API authentication failures
    - Rate limiting
    - Invalid requests
    - Provider unavailability
    """
    pass


class WorkflowError(Exception):
    """
    Exception for workflow-related errors.

    Raised when the workflow orchestrator encounters errors such as:
    - Invalid workflow state
    - Task execution failures
    - Agent coordination issues
    - Pipeline interruptions
    """
    pass


class ResearchError(Exception):
    """
    Exception for research-related errors.

    Raised when the research agent encounters errors such as:
    - Search API failures
    - Information retrieval issues
    - Source validation failures
    - Data parsing errors
    """
    pass


class MemoryError(Exception):
    """
    Exception for memory-related errors.

    Raised when the memory system encounters errors such as:
    - Vector store connection failures
    - Memory retrieval errors
    - Storage capacity issues
    - Index corruption
    """
    pass


class ConfigurationError(Exception):
    """
    Exception for configuration-related errors.

    Raised when the configuration loader encounters errors such as:
    - Missing required environment variables
    - Invalid configuration values
    - Configuration file parsing errors
    - Validation failures
    """
    pass
