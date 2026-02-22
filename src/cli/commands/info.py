"""stackfordev info command — display supported languages, stacks, and versions."""

import click
from rich.console import Console
from rich.table import Table

from src.cli.config import LANGUAGE_VERSIONS, LANGUAGE_STACKS


@click.command()
def info():
    """Show supported languages, versions, and stacks."""
    console = Console()
    table = Table(title="StackForDev — Supported Configurations", show_lines=True)
    table.add_column("Language", style="bold cyan", no_wrap=True)
    table.add_column("Versions", style="green")
    table.add_column("Stacks", style="yellow")

    for lang in LANGUAGE_VERSIONS:
        versions = ", ".join(LANGUAGE_VERSIONS[lang])
        stacks = "\n".join(LANGUAGE_STACKS[lang])
        table.add_row(lang, versions, stacks)

    console.print(table)
