"""OpenRouter-compatible LLM client with bounded retries.

A single client instance is created during application startup and shared by
every agent, so connection pools and instrumentation live in one place.
"""

import random
import time
from typing import Any, Dict, List, Optional

from openai import (
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    OpenAI,
    PermissionDeniedError,
)

from backend.core.config import Settings, get_settings
from backend.core.exceptions import LLMError
from backend.core.logger import get_logger

logger = get_logger(__name__)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

#: Client/configuration errors that retrying cannot fix. These fail fast so a
#: bad key or malformed request does not burn the whole retry budget. Rate
#: limits, timeouts, connection failures and 5xx responses remain retryable.
_NON_RETRYABLE_ERRORS = (
    AuthenticationError,
    PermissionDeniedError,
    BadRequestError,
    NotFoundError,
)

#: Upper bound on an error message we keep on an :class:`LLMError`.
_MAX_ERROR_DETAIL = 500


class LLMClient:
    """Thin wrapper over the OpenAI-compatible OpenRouter chat completions API."""

    def __init__(self, settings: Optional[Settings] = None, client: Optional[Any] = None):
        self.settings = settings or get_settings()
        self.client = client or OpenAI(api_key=self.settings.OPENROUTER_API_KEY,
                                       base_url=OPENROUTER_BASE_URL,
                                       timeout=self.settings.LLM_TIMEOUT_SECONDS)
        self.model = self.settings.MODEL_NAME
        self.temperature = self.settings.TEMPERATURE
        self.max_tokens = self.settings.MAX_TOKENS
        self.max_retries = self.settings.LLM_MAX_RETRIES

    def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
        """Send a chat completion request, retrying a bounded number of times.

        Non-retryable client errors (authentication, permissions, malformed
        requests, unknown model) fail immediately. Transient failures use
        exponential backoff with a small jitter.
        """

        last_error: Optional[BaseException] = None
        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=model or self.model, messages=messages,
                    temperature=self.temperature, max_tokens=self.max_tokens)
                content = response.choices[0].message.content
                if not content:
                    raise LLMError("The model returned an empty response.")
                return content
            except LLMError:
                # An empty-content guard is deterministic: never retry it.
                raise
            except Exception as error:
                last_error = error
                if isinstance(error, _NON_RETRYABLE_ERRORS):
                    logger.warning("LLM request rejected with non-retryable %s",
                                   type(error).__name__)
                    raise LLMError(self._error_message(error)) from error
                if attempt >= self.max_retries:
                    logger.exception("LLM request failed after retries")
                    raise LLMError(self._error_message(error)) from error
                time.sleep(self._backoff_delay(attempt))

        # Defensive: the loop either returns or raises above.
        raise LLMError(self._error_message(last_error))

    @staticmethod
    def _backoff_delay(attempt: int) -> float:
        """Exponential-ish backoff with jitter to avoid thundering herds."""

        return 0.5 * (attempt + 1) + random.uniform(0, 0.25)

    @staticmethod
    def _error_message(error: Optional[BaseException]) -> str:
        """Build a safe, bounded message. Provider payloads never contain keys."""

        detail = str(error).strip() if error else ""
        if not detail:
            return "The AI provider could not complete this request."
        return (
            "The AI provider could not complete this request: "
            f"{detail[:_MAX_ERROR_DETAIL]}"
        )

    def switch_model(self, model_name: str) -> None:
        if not model_name or not model_name.strip():
            raise ValueError("Model name cannot be empty.")
        self.model = model_name.strip()
