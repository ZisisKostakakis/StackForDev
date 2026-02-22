"""Tests for CLI config consistency."""

import pytest

from src.cli.config import (
    LANGUAGE_VERSIONS,
    LANGUAGE_STACKS,
    validate_language,
    validate_version,
    validate_stack,
)
from src.generator_core import STACK_PACKAGES, SUPPORTED_LANGUAGES


def test_all_languages_have_versions():
    for lang in SUPPORTED_LANGUAGES:
        assert lang in LANGUAGE_VERSIONS, f"{lang} missing from LANGUAGE_VERSIONS"


def test_all_languages_have_stacks():
    for lang in SUPPORTED_LANGUAGES:
        assert lang in LANGUAGE_STACKS, f"{lang} missing from LANGUAGE_STACKS"


def test_all_stacks_have_packages():
    for lang, stacks in LANGUAGE_STACKS.items():
        for stack in stacks:
            assert stack in STACK_PACKAGES, f"Stack '{stack}' for {lang} missing from STACK_PACKAGES"


def test_validate_language_valid():
    assert validate_language("Python") == "python"


def test_validate_language_invalid():
    with pytest.raises(ValueError, match="Unsupported language"):
        validate_language("COBOL")


def test_validate_version_valid():
    assert validate_version("python", "3.11") == "3.11"


def test_validate_version_invalid():
    with pytest.raises(ValueError, match="Unsupported version"):
        validate_version("python", "2.7")


def test_validate_stack_valid():
    assert validate_stack("python", "Django Stack") == "Django Stack"


def test_validate_stack_invalid():
    with pytest.raises(ValueError, match="Unsupported stack"):
        validate_stack("python", "Nonexistent")
