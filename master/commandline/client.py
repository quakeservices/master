import socket
from typing import Optional

import click

from master.protocols.models import BaseProtocolHeader
from master.protocols.models.game import GameProtocol
from master.protocols.models.idtech2.quake2 import Quake2

DEFAULT_HOST: str = socket.gethostbyname(socket.gethostname())
DEFAULT_PORT: int = 27900
DEFAULT_TIMEOUT: float = 30.0
DEFAULT_SIZE: int = 1024
CLIENT: GameProtocol = Quake2()
CHOICES: list[str] = list(CLIENT.headers.keys())

# \\cheats\\0\\deathmatch\\1\\dmflags\\16\\fraglimit\\0\\gamedate\\Dec 23 2019\\gamename\\baseq2\\hostname\\noname\\mapname\\q2dm1\\maxclients\\8\\maxspectators\\4\\needpass\\0\\protocol\\34\\timelimit\\0\\version\\7.43pre x86_64 Dec 23 2019 Linux\n
def build_payload(header: bytes, data: tuple[tuple[str]]) -> bytes:
    newline: bytes = CLIENT.newline.encode(CLIENT.encoding)
    string_data: str = CLIENT.split.join([CLIENT.split.join(datum) for datum in data])

    return newline.join([header, string_data.encode(CLIENT.encoding)])


@click.group()
def client_cli() -> None:
    pass


@client_cli.command()
@click.option(
    "-h", "--host", "host", default=DEFAULT_HOST, type=str, help=("Host to connect to")
)
@click.option(
    "-p", "--port", "port", default=DEFAULT_PORT, type=int, help=("Port to connect to")
)
@click.option(
    "-t",
    "--timeout",
    "timeout",
    default=DEFAULT_TIMEOUT,
    type=float,
    help=("How long to wait (in seconds) to receive a response"),
)
@click.option(
    "-b",
    "--buffer",
    "buffer",
    default=DEFAULT_SIZE,
    type=int,
    help=("Amount of data expected to be returned."),
)
@click.option(
    "-r",
    "--request",
    "request",
    type=click.Choice(CHOICES, case_sensitive=False),
    default=CHOICES[0],
    help=("Type of request to send"),
)
@click.option(
    "-d",
    "--data",
    "data",
    nargs=2,
    type=str,
    multiple=True,
    default=None,
    help=("Data to send with the request"),
)
@click.option(
    "-w",
    "--wait-for-response",
    "wait_for_response",
    is_flag=True,
    default=False,
    help=(
        "Wait for response even if there is no response expected."
        "Useful for requests that don't have a response defined but will return something."
    ),
)
def client(
    host: str,
    port: int,
    request: str,
    data: tuple[tuple[str]],
    timeout: float,
    buffer: int,
    wait_for_response: bool,
) -> tuple[Optional[bytes], bytes]:
    """
    Sends a request (header.received) and returns the expected
    response (header.response) and actual response
    """
    header: BaseProtocolHeader = CLIENT.headers.get(request)
    sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)

    click.echo(f"Connecting to {host}:{port}...")
    payload: bytes = build_payload(header.received, data)
    sock.sendto(payload, (host, port))
    click.echo(f"Sent:       {payload!r}")

    request_response: Optional[bytes] = None
    if header.response:
        click.echo(f"Expecting:  {header.response!r}")

    if header.response or wait_for_response:
        request_response = sock.recv(buffer)
        click.echo(f"Received:   {request_response!r}")

    return header.response, request_response
