"""Interactive prompts for when CLI flags are missing."""

from rich.console import Console
from rich.prompt import Prompt

from src.cli.config import LANGUAGE_VERSIONS, LANGUAGE_STACKS


def prompt_config(
    language: str | None = None,
    lang_version: str | None = None,
    stack: str | None = None,
) -> tuple[str, str, str, list[str]]:
    """Prompt the user interactively for missing config values.

    Returns:
        (language, version, stack, extras_list)
    """
    console = Console()
    console.print("[bold]StackForDev[/] — Generate a Dockerfile\n")

    languages = list(LANGUAGE_VERSIONS.keys())
    if language is None:
        console.print("Available languages:")
        for i, l in enumerate(languages, 1):
            console.print(f"  {i}. {l}")
        raw = Prompt.ask("Select language", choices=[str(i) for i in range(1, len(languages) + 1)], default="1")
        language = languages[int(raw) - 1]
    language = language.lower()

    versions = LANGUAGE_VERSIONS[language]
    if lang_version is None:
        console.print("\nAvailable versions:")
        for i, v in enumerate(versions, 1):
            console.print(f"  {i}. {v}")
        raw = Prompt.ask("Select version", choices=[str(i) for i in range(1, len(versions) + 1)], default="1")
        lang_version = versions[int(raw) - 1]

    stacks = LANGUAGE_STACKS[language]
    if stack is None:
        console.print("\nAvailable stacks:")
        for i, s in enumerate(stacks, 1):
            console.print(f"  {i}. {s}")
        number_choices = [str(i) for i in range(1, len(stacks) + 1)]
        raw = Prompt.ask("Select stack", choices=number_choices, default="1")
        stack = stacks[int(raw) - 1]

    extras_input = Prompt.ask("Extra dependencies (comma-separated, Enter to skip)", default="")
    extras_list = [e.strip() for e in extras_input.split(",") if e.strip()]

    return language, lang_version, stack, extras_list
