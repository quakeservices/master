import click

from master.commandline.client import client_cli
from master.commandline.schema import schema_cli
from master.commandline.server import server_cli
from master.helpers import setup_environment, setup_logging


@click.command(
    cls=click.CommandCollection, sources=[server_cli, client_cli, schema_cli]
)
@click.option(
    "--log-level",
    type=click.Choice(["info", "warn", "debug"], case_sensitive=False),
    default="info",
)
@click.option("--boto-logs/--no-boto-logs", default=False)
def cli(log_level: str, boto_logs: bool) -> None:
    setup_environment()
    setup_logging(log_level, boto_logs)
