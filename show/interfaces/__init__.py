"""SONiC show interfaces command group."""

import click


@click.group(name="interfaces")
def interfaces():
    """Show interface information."""
