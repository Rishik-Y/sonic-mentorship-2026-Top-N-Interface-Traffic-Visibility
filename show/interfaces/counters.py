"""SONiC show interfaces counters command group."""

import click


@click.group(name="counters")
def counters():
    """Show interface counters."""
