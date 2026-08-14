"""OpenRouter-compatible LLM client with bounded retries."""

import time

from openai import OpenAI

from backend.core.config import settings
from backend.core.exceptions import LLMError
from backend.core.logger import get_logger

logger = get_logger(__name__)


class LLMClient:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENROUTER_API_KEY,
                             base_url="https://openrouter.ai/api/v1",
                             timeout=settings.LLM_TIMEOUT_SECONDS)
        self.model = settings.MODEL_NAME
        self.temperature = settings.TEMPERATURE
        self.max_tokens = settings.MAX_TOKENS

    def chat(self, messages, model=None):
        for attempt in range(settings.LLM_MAX_RETRIES + 1):
            try:
                response = self.client.chat.completions.create(
                    model=model or self.model, messages=messages,
                    temperature=self.temperature, max_tokens=self.max_tokens)
                content = response.choices[0].message.content
                if not content:
                    raise LLMError("The model returned an empty response.")
                return content
            except Exception as error:
                if attempt >= settings.LLM_MAX_RETRIES:
                    logger.exception("LLM request failed after retries")
                    raise LLMError("The AI provider could not complete this request.") from error
                time.sleep(0.5 * (attempt + 1))

    def switch_model(self, model_name):
        if not model_name or not model_name.strip():
            raise ValueError("Model name cannot be empty.")
        self.model = model_name.strip()
