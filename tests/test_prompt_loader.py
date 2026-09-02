"""Prompt loading, caching, and error handling."""

import pytest

from backend.utils.prompt_loader import PROMPTS_DIR, clear_prompt_cache, load_prompt

ACTIVE_PROMPTS = ["planner.md", "researcher.md", "verifier.md", "writer.md"]


@pytest.fixture(autouse=True)
def _clear_cache():
    clear_prompt_cache()
    yield
    clear_prompt_cache()


@pytest.mark.parametrize("filename", ACTIVE_PROMPTS)
def test_active_prompts_exist_and_are_not_empty(filename):
    content = load_prompt(filename)
    assert content
    assert content == content.strip()


@pytest.mark.parametrize("filename", ACTIVE_PROMPTS)
def test_prompt_files_live_in_the_prompts_directory(filename):
    assert (PROMPTS_DIR / filename).exists()


def test_missing_prompt_raises_file_not_found():
    with pytest.raises(FileNotFoundError) as error:
        load_prompt("does_not_exist.md")
    assert "does_not_exist.md" in str(error.value)


def test_empty_prompt_raises_value_error(tmp_path, monkeypatch):
    empty = tmp_path / "empty.md"
    empty.write_text("   \n", encoding="utf-8")
    monkeypatch.setattr("backend.utils.prompt_loader.PROMPTS_DIR", tmp_path)
    clear_prompt_cache()

    with pytest.raises(ValueError):
        load_prompt("empty.md")


def test_prompts_are_cached(tmp_path, monkeypatch):
    prompt = tmp_path / "cached.md"
    prompt.write_text("first", encoding="utf-8")
    monkeypatch.setattr("backend.utils.prompt_loader.PROMPTS_DIR", tmp_path)
    clear_prompt_cache()

    assert load_prompt("cached.md") == "first"
    prompt.write_text("second", encoding="utf-8")
    assert load_prompt("cached.md") == "first"

    clear_prompt_cache()
    assert load_prompt("cached.md") == "second"


def test_planner_prompt_forbids_answering():
    content = load_prompt("planner.md").lower()
    assert "research plan" in content
