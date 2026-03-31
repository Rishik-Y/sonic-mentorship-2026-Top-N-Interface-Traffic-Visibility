"""CLI entrypoint for Top-N interface visibility feature."""

import click

from show import show
from show.interfaces import interfaces
from show.interfaces.counters import counters
from show.interfaces.top_n import top_n as top_n_command


@click.group()
def cli():
    """Root CLI command group."""


# Native tree: show interfaces counters top-n
show.add_command(interfaces)
interfaces.add_command(counters)
counters.add_command(top_n_command)
cli.add_command(show)

# Backward-compatibility alias retained for prototype scripts.
top_n = top_n_command
cli.add_command(top_n_command, name="top-n")


if __name__ == "__main__":
    cli()
