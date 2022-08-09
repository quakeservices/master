import click

from master.client.main import _generate_request
from master.constants import (
    DEFAULT_BUFFER,
    DEFAULT_CLIENT_ADDRESS,
    DEFAULT_CLIENT_PORT,
    DEFAULT_HOST_ADDRESS,
    DEFAULT_HOST_PORT,
    DEFAULT_TIMEOUT,
)
from master.protocols.models.game import GameProtocol
from master.protocols.models.idtech2.quake2 import Quake2

PROTOCOLS: dict[str, GameProtocol] = {"quake2": Quake2()}
PROTOCOL_CHOICES: list[str] = list(PROTOCOLS.keys())
DEFAULT_PROTOCOL_CHOICE: str = PROTOCOL_CHOICES[0]
DEFAULT_REQUEST_CHOICES: list[str] = ["ping", "heartbeat", "shutdown", "query"]


@click.group()
def client_cli() -> None:
    pass


@client_cli.group()
def client() -> None:
    """
    Client operations
    """


@client.command()
@click.option(
    "--protocol",
    type=click.Choice(PROTOCOL_CHOICES, case_sensitive=False),
    default=DEFAULT_PROTOCOL_CHOICE,
    help=("GameProtocol to use"),
)
@click.option(
    "--host",
    default=DEFAULT_HOST_ADDRESS,
    type=str,
    help=("Host to connect to"),
)
@click.option(
    "--port",
    default=DEFAULT_HOST_PORT,
    type=int,
    help=("Port to connect to"),
)
@click.option(
    "--client-host",
    default=DEFAULT_CLIENT_ADDRESS,
    type=str,
    help=("Host to connect from"),
)
@click.option(
    "--client-port",
    default=DEFAULT_CLIENT_PORT,
    type=int,
    help=("Port to connect from"),
)
@click.option(
    "--timeout",
    default=DEFAULT_TIMEOUT,
    type=float,
    help=("How long to wait (in seconds) to receive a response"),
)
@click.option(
    "--buffer",
    default=DEFAULT_BUFFER,
    type=int,
    help=("Amount of data expected to be returned."),
)
@click.option(
    "--request",
    type=click.Choice(DEFAULT_REQUEST_CHOICES, case_sensitive=False),
    default=DEFAULT_REQUEST_CHOICES[0],
    help=("Type of request to send"),
)
@click.option(
    "--data",
    nargs=2,
    type=str,
    multiple=True,
    default=None,
    help=("Data to send with the request"),
)
@click.option(
    "--wait-for-response",
    is_flag=True,
    default=False,
    help=(
        "Wait for response even if there is no response expected."
        "Useful for requests that don't have a response defined but will return something."
    ),
)
@click.option("--quiet", is_flag=True)
def send(
    protocol: str,
    host: str,
    port: int,
    client_host: str,
    client_port: int,
    request: str,
    data: tuple[tuple[str]],
    timeout: float,
    buffer: int,
    wait_for_response: bool,
    quiet: bool,
) -> None:
    """
    Sends a request (header.received) and returns the expected
    response (header.response) and actual response
    """
    _generate_request(
        protocol=PROTOCOLS[protocol],
        host=host,
        port=port,
        client_host=client_host,
        client_port=client_port,
        request=request,
        data=data,
        timeout=timeout,
        buffer=buffer,
        wait_for_response=wait_for_response,
        quiet=quiet,
    )
