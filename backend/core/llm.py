"""OpenRouter-compatible LLM client with bounded retries.

A single client instance is created during application startup and shared by
every agent, so connection pools and instrumentation live in one place.
"""

import time
from typing import Any, Dict, List, Optional

from openai import OpenAI

from backend.core.config import Settings, get_settings
from backend.core.exceptions import LLMError
from backend.core.logger import get_logger

logger = get_logger(__name__)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


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
        """Send a chat completion request, retrying a bounded number of times."""

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
            except Exception as error:
                last_error = error
                if attempt >= self.max_retries:
                    logger.exception("LLM request failed after retries")
                    raise LLMError("The AI provider could not complete this request.") from error
                time.sleep(0.5 * (attempt + 1))

        # Defensive: the loop either returns or raises above.
        raise LLMError("The AI provider could not complete this request.") from last_error

    def switch_model(self, model_name: str) -> None:
        if not model_name or not model_name.strip():
            raise ValueError("Model name cannot be empty.")
        self.model = model_name.strip()
