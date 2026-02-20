"""Rich display helpers for CLI output."""

import sys

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax


def is_tty() -> bool:
    return sys.stdout.isatty()


def print_dockerfile(content: str, language: str, stack: str) -> None:
    """Print Dockerfile with Rich syntax highlighting if TTY, raw otherwise."""
    if not is_tty():
        sys.stdout.write(content)
        return

    console = Console()
    syntax = Syntax(content, "dockerfile", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title=f"[bold green]Dockerfile — {language} / {stack}[/]", border_style="green"))
    console.print()
    console.print("[dim]Tip: docker build -t myapp -f Dockerfile . && docker run -it -v $(pwd):/usr/src/app myapp[/]")


def print_saved(path: str) -> None:
    console = Console(stderr=True)
    console.print(f"[green]Saved to {path}[/]")
