"""CLI configuration: language versions, stacks, and validation."""

from src.generator_core import STACK_PACKAGES

LANGUAGE_VERSIONS: dict[str, list[str]] = {
    "python": ["3.12", "3.11", "3.10", "3.9"],
    "javascript": ["22", "20", "18"],
    "go": ["1.23", "1.22", "1.21"],
}

LANGUAGE_STACKS: dict[str, list[str]] = {
    "python": ["Django Stack", "Flask Stack", "Data Science Stack", "Web Scraping Stack", "Machine Learning Stack"],
    "javascript": ["Express Stack", "React Stack", "Vue.js Stack", "Node.js API Stack", "Full-Stack JavaScript"],
    "go": ["Gin Stack", "Beego Stack", "Web Framework Stack", "Microservices Stack", "Data Processing Stack"],
}

API_URL = "https://f88slnkaa6.execute-api.eu-west-2.amazonaws.com/prod/cli/generate-dockerfile"


def validate_language(language: str) -> str:
    lang = language.lower()
    if lang not in LANGUAGE_VERSIONS:
        raise ValueError(f"Unsupported language: {language}. Supported: {', '.join(LANGUAGE_VERSIONS)}")
    return lang


def validate_version(language: str, version: str) -> str:
    versions = LANGUAGE_VERSIONS[language]
    if version not in versions:
        raise ValueError(f"Unsupported version '{version}' for {language}. Supported: {', '.join(versions)}")
    return version


def validate_stack(language: str, stack: str) -> str:
    stacks = LANGUAGE_STACKS[language]
    if stack not in stacks:
        raise ValueError(f"Unsupported stack '{stack}' for {language}. Supported: {', '.join(stacks)}")
    return stack
