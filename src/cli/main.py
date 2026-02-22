"""StackForDev CLI entrypoint."""

import click

from src.cli.commands.generate import generate
from src.cli.commands.info import info
from src.cli.commands.init import init


@click.group()
@click.version_option(package_name="stackfordev")
def cli():
    """StackForDev — Generate tailored Dockerfiles for development environments."""


cli.add_command(generate)
cli.add_command(info)
cli.add_command(init)
