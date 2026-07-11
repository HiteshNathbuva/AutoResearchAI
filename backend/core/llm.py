"""
LLM Abstraction Module

This module provides a unified interface for interacting with Large Language Models.
It abstracts the complexity of different LLM providers and offers a consistent API.

Current Provider:
- OpenRouter (Primary)

Future Enhancements:
- Streaming support
- Retry mechanism
- Multiple provider support (OpenAI, Anthropic, Gemini, etc.)
- Model switching
"""

from openai import OpenAI

from backend.core.config import settings


class LLMClient:
    """
    Unified LLM client for interacting with language models.

    This class provides a consistent interface for making requests to
    various LLM providers, starting with OpenRouter.
    """

    def __init__(self):
        """
        Initialize the LLM client using application configuration.
        """

        self.client = OpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )

        self.model = settings.MODEL_NAME
        self.temperature = settings.TEMPERATURE
        self.max_tokens = settings.MAX_TOKENS

    def chat(self, messages, model=None):
        """
        Send a chat completion request to the LLM.

        Args:
            messages (list):
                List of message dictionaries.

            model (str, optional):
                Override the default model.

        Returns:
            str:
                Assistant response.
        """

        response = self.client.chat.completions.create(
            model=model or self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        return response.choices[0].message.content

    def stream(self, messages, model=None):
        """
        Stream chat completion responses in real-time.

        Args:
            messages:
                List of message dictionaries.

            model:
                Optional model override.

        Yields:
            Streaming response chunks.

        TODO:
        - Implement OpenRouter streaming
        - Yield response chunks
        - Handle interruptions
        """

        raise NotImplementedError(
            "Streaming support has not been implemented yet."
        )

    def retry_request(self, request_func, max_retries=3):
        """
        Retry failed requests.

        Args:
            request_func:
                Callable request function.

            max_retries:
                Maximum retry attempts.

        Returns:
            Successful response.

        TODO:
        - Implement exponential backoff
        - Retry transient failures
        - Handle rate limits
        """

        raise NotImplementedError(
            "Retry mechanism has not been implemented yet."
        )

    def switch_model(self, model_name):
        """
        Switch the active LLM model.

        Args:
            model_name:
                New model name.

        TODO:
        - Validate model
        - Update configuration
        - Handle provider-specific settings
        """

        self.model = model_name