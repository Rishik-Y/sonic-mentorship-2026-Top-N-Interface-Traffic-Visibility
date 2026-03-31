"""SONiC show CLI root group."""

import click


@click.group()
def show():
    """Show running system state."""
