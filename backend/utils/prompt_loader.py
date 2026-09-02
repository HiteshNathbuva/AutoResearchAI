"""
Prompt Loader Utility

Loads prompt templates from the prompts directory. Results are cached because
prompt files are read on every agent invocation and do not change at runtime.
"""

from functools import lru_cache
from pathlib import Path

# Project Root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Prompts Folder
PROMPTS_DIR = PROJECT_ROOT / "prompts"


@lru_cache(maxsize=32)
def load_prompt(filename: str) -> str:
    """
    Load a prompt file from the prompts directory.

    Args:
        filename: Name of the prompt file.

    Returns:
        Prompt content as a string.

    Raises:
        FileNotFoundError: If the prompt file does not exist.
        ValueError: If the prompt file is empty.
    """

    prompt_path = PROMPTS_DIR / filename

    if not prompt_path.exists():
        raise FileNotFoundError(
            f"Prompt file '{filename}' not found in {PROMPTS_DIR}"
        )

    content = prompt_path.read_text(encoding="utf-8").strip()

    if not content:
        raise ValueError(f"Prompt file '{filename}' is empty.")

    return content


def clear_prompt_cache() -> None:
    """Clear the prompt cache (used by tests and future hot-reloading)."""

    load_prompt.cache_clear()
