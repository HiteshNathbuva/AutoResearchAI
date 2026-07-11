"""
Prompt Loader Utility

Loads prompt templates from the prompts directory.
"""

from pathlib import Path


# Project Root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Prompts Folder
PROMPTS_DIR = PROJECT_ROOT / "prompts"


def load_prompt(filename: str) -> str:
    """
    Load a prompt file from the prompts directory.

    Args:
        filename: Name of the prompt file.

    Returns:
        Prompt content as a string.

    Raises:
        FileNotFoundError: If the prompt file does not exist.
    """

    prompt_path = PROMPTS_DIR / filename

    if not prompt_path.exists():
        raise FileNotFoundError(
            f"Prompt file '{filename}' not found in {PROMPTS_DIR}"
        )

    return prompt_path.read_text(
        encoding="utf-8"
    ).strip()