"""stackfordev generate command."""

import json
import os
import sys

import click

from src.cli.config import (
    validate_language,
    validate_version,
    validate_stack,
)
from src.cli.display import print_dockerfile, print_saved
from src.generator_core import GenerateDockerfileRequest, DockerfileGenerator
from src.docker_templates.compose_template import COMPOSE_TEMPLATE, DOCKERIGNORE_TEMPLATE


@click.command()
@click.option("--language", "-l", type=str, default=None, help="Language: python, javascript, go")
@click.option("--stack", "-s", type=str, default=None, help="Dependency stack (e.g. 'Django Stack')")
@click.option("--version", "-v", "lang_version", type=str, default=None, help="Language version (e.g. 3.11)")
@click.option("--extras", "-e", type=str, default=None, help="Comma-separated extra dependencies")
@click.option("--output", "-o", type=click.Path(), default=None, help="Save Dockerfile to path")
@click.option("--local", is_flag=True, default=False, help="Generate offline (no API call)")
@click.option("--json-output", "--json", "json_mode", is_flag=True, default=False, help="Output raw JSON")
@click.option("--compose", is_flag=True, default=False, help="Also generate docker-compose.yml and .dockerignore")
def generate(language, stack, lang_version, extras, output, local, json_mode, compose):
    """Generate a Dockerfile for a development environment."""
    # If any flag is missing and we're in a TTY, go interactive
    if (language is None or stack is None or lang_version is None) and sys.stdin.isatty():
        from src.cli.interactive import prompt_config
        language, lang_version, stack, extras_list = prompt_config(language, lang_version, stack)
    elif language is None or stack is None or lang_version is None:
        click.echo(
            "Error: --language, --stack, and --version are required in non-interactive mode.\n"
            "Example: stackfordev generate -l python -s 'Django Stack' -v 3.11",
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

    if local:
        generator = DockerfileGenerator(config=config)
        dockerfile_content = generator.generate_dockerfile()
    else:
        try:
            from src.cli.api_client import generate_via_api
            result = generate_via_api(config)
            dockerfile_content = result["dockerfile"]
        except Exception as e:
            click.echo(f"API error: {e}\nTip: use --local to generate offline.", err=True)
            sys.exit(1)

    if json_mode:
        click.echo(json.dumps({
            "language": lang,
            "stack": stack,
            "version": lang_version,
            "dockerfile": dockerfile_content,
        }))
        return

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(dockerfile_content)
        print_saved(output)

        if compose:
            output_dir = os.path.dirname(os.path.abspath(output))
            project_name = os.path.basename(output_dir) or lang

            compose_path = os.path.join(output_dir, "docker-compose.yml")
            with open(compose_path, "w", encoding="utf-8") as f:
                f.write(COMPOSE_TEMPLATE.format(project_name=project_name))
            print_saved(compose_path)

            dockerignore_path = os.path.join(output_dir, ".dockerignore")
            with open(dockerignore_path, "w", encoding="utf-8") as f:
                f.write(DOCKERIGNORE_TEMPLATE)
            print_saved(dockerignore_path)
        return

    if compose:
        click.echo("--- docker-compose.yml ---")
        click.echo(COMPOSE_TEMPLATE.format(project_name=lang))
        click.echo("--- .dockerignore ---")
        click.echo(DOCKERIGNORE_TEMPLATE)

    print_dockerfile(dockerfile_content, lang, stack)
