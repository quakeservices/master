import logging

import click

from master.server import MasterServer


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
    logging.info("Starting master server.")

    masterserver = MasterServer()
    masterserver.initialise()
    masterserver.start()

    logging.info("Master server stopped.")
