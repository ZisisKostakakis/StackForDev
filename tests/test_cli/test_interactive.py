"""Tests for interactive mode prompts."""

from unittest.mock import patch

from src.cli.interactive import prompt_config


@patch("src.cli.interactive.Prompt.ask")
def test_prompt_config_full_prompts(mock_ask):
    mock_ask.side_effect = [
        "1",   # language (python)
        "2",   # version (3.11)
        "1",   # stack (Django Stack)
        "",    # extras
    ]
    lang, ver, stack, extras = prompt_config()
    assert lang == "python"
    assert ver == "3.11"
    assert stack == "Django Stack"
    assert extras == []


@patch("src.cli.interactive.Prompt.ask")
def test_prompt_config_with_extras(mock_ask):
    mock_ask.side_effect = [
        "1",   # python
        "2",   # 3.11
        "1",   # Django Stack
        "numpy, pandas",
    ]
    lang, ver, stack, extras = prompt_config()
    assert extras == ["numpy", "pandas"]


@patch("src.cli.interactive.Prompt.ask")
def test_prompt_config_partial_flags(mock_ask):
    """When language is pre-provided, should skip that prompt."""
    mock_ask.side_effect = [
        "2",   # version (3.11)
        "2",   # stack (Flask Stack)
        "",    # extras
    ]
    lang, ver, stack, extras = prompt_config(language="python")
    assert lang == "python"
    assert ver == "3.11"
    assert stack == "Flask Stack"
