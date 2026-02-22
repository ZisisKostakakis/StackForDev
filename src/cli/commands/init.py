"""stackfordev init command — bootstrap a full containerised dev workspace."""

import os
import sys

import click
from rich.console import Console

from src.cli.config import validate_language, validate_version, validate_stack
from src.cli.display import print_saved
from src.generator_core import GenerateDockerfileRequest, DockerfileGenerator
from src.docker_templates.compose_template import COMPOSE_TEMPLATE, DOCKERIGNORE_TEMPLATE
from src.docker_templates.shell_template import SHELL_TEMPLATE


@click.command()
@click.option("--language", "-l", type=str, default=None, help="Language: python, javascript, go, rust, java")
@click.option("--stack", "-s", type=str, default=None, help="Dependency stack (e.g. 'Django Stack')")
@click.option("--version", "-v", "lang_version", type=str, default=None, help="Language version (e.g. 3.12)")
@click.option("--extras", "-e", type=str, default=None, help="Comma-separated extra dependencies")
@click.option(
    "--directory", "-d", "target_dir",
    type=click.Path(), default=".",
    help="Target directory for generated files (default: current directory)"
)
def init(language, stack, lang_version, extras, target_dir):
    """Bootstrap a full containerised dev workspace.

    Generates: Dockerfile, docker-compose.yml, .dockerignore, devrun.sh
    """
    console = Console()

    if (language is None or stack is None or lang_version is None) and sys.stdin.isatty():
        from src.cli.interactive import prompt_config
        language, lang_version, stack, extras_list = prompt_config(language, lang_version, stack)
    elif language is None or stack is None or lang_version is None:
        click.echo(
            "Error: --language, --stack, and --version are required in non-interactive mode.",
            err=True,
        )
        sys.exit(1)
    else:
        extras_list = [e.strip() for e in extras.split(",") if e.strip()] if extras else []

    try:
        lang = validate_language(language)
        validate_version(lang, lang_version)
        validate_stack(lang, stack)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    config = GenerateDockerfileRequest(
        language=lang,
        dependency_stack=stack,
        extra_dependencies=extras_list,
        language_version=lang_version,
    )

    generator = DockerfileGenerator(config=config)
    dockerfile_content = generator.generate_dockerfile()

    target = os.path.abspath(target_dir)
    os.makedirs(target, exist_ok=True)
    project_name = os.path.basename(target) or lang

    files = {
        "Dockerfile": dockerfile_content,
        "docker-compose.yml": COMPOSE_TEMPLATE.format(project_name=project_name),
        ".dockerignore": DOCKERIGNORE_TEMPLATE,
        "devrun.sh": SHELL_TEMPLATE,
    }

    for filename, content in files.items():
        path = os.path.join(target, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print_saved(path)

    console.print()
    console.print("[bold green]Workspace ready![/] Next steps:")
    console.print(f"  [cyan]docker compose build[/]")
    console.print(f"  [cyan]source {os.path.join(target_dir, 'devrun.sh')}[/]")
    console.print(f"  [cyan]devrun {lang} --version[/]")
