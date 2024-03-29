import click

from master.commandline.client import client_cli
from master.commandline.database import database_cli
from master.commandline.server import server_cli
from master.helpers import setup_environment, setup_logging

# from master.commandline.schema import schema_cli


@click.command(
    cls=click.CommandCollection,
    sources=[server_cli, client_cli, database_cli],
)
@click.option(
    "--log-level",
    type=click.Choice(["info", "warn", "debug"], case_sensitive=False),
    default="info",
)
@click.option("--hide-boto-logs", is_flag=True)
def cli(log_level: str, hide_boto_logs: bool) -> None:
    setup_environment()
    setup_logging(log_level, hide_boto_logs)
