"""StackForDev CLI entrypoint."""

import click

from src.cli.commands.generate import generate


@click.group()
@click.version_option(package_name="stackfordev")
def cli():
    """StackForDev — Generate tailored Dockerfiles for development environments."""


cli.add_command(generate)
