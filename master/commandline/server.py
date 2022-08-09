import click

from master.server.main import _run


@click.group()
def server_cli() -> None:
    pass


@server_cli.group()
def server() -> None:
    """
    Server operations
    """


@server.command()
def run() -> None:
    """
    Run the masterserver
    """
    _run()
