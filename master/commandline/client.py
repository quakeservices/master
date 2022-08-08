import socket
from typing import Optional

import click

from master.protocols.models import BaseProtocolHeader
from master.protocols.models.game import GameProtocol
from master.protocols.models.idtech2.quake2 import Quake2

DEFAULT_HOST_ADDRESS: str = socket.gethostbyname(socket.gethostname())
DEFAULT_HOST_PORT: int = 27900
DEFAULT_CLIENT_ADDRESS: str = "0.0.0.0"
DEFAULT_CLIENT_PORT: int = 27910
DEFAULT_TIMEOUT: float = 30.0
DEFAULT_BUFFER: int = 1024
CLIENT: GameProtocol = Quake2()
CHOICES: list[str] = list(CLIENT.headers.keys())
DEFAULT_CHOICE: str = CHOICES[0]


@click.group()
def client_cli() -> None:
    pass


@client_cli.command()
@click.option(
    "-h",
    "--host",
    default=DEFAULT_HOST_ADDRESS,
    type=str,
    help=("Host to connect to"),
)
@click.option(
    "-p",
    "--port",
    default=DEFAULT_HOST_PORT,
    type=int,
    help=("Port to connect to"),
)
@click.option(
    "-t",
    "--timeout",
    default=DEFAULT_TIMEOUT,
    type=float,
    help=("How long to wait (in seconds) to receive a response"),
)
@click.option(
    "-b",
    "--buffer",
    default=DEFAULT_BUFFER,
    type=int,
    help=("Amount of data expected to be returned."),
)
@click.option(
    "-r",
    "--request",
    type=click.Choice(CHOICES, case_sensitive=False),
    default=CHOICES[0],
    help=("Type of request to send"),
)
@click.option(
    "-d",
    "--data",
    nargs=2,
    type=str,
    multiple=True,
    default=None,
    help=("Data to send with the request"),
)
@click.option(
    "-w",
    "--wait-for-response",
    is_flag=True,
    default=False,
    help=(
        "Wait for response even if there is no response expected."
        "Useful for requests that don't have a response defined but will return something."
    ),
)
@click.option("--quiet", is_flag=True)
def client(
    host: str,
    port: int,
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
        host=host,
        port=port,
        request=request,
        data=data,
        timeout=timeout,
        buffer=buffer,
        wait_for_response=wait_for_response,
        quiet=quiet,
    )


def _setup_socket(timeout: float, quiet: bool) -> socket.socket:
    sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    if not quiet:
        click.echo(
            f"Binding client to {DEFAULT_CLIENT_ADDRESS}:{DEFAULT_CLIENT_PORT}..."
        )

    try:
        sock.bind((DEFAULT_CLIENT_ADDRESS, DEFAULT_CLIENT_PORT))
    except OSError:
        click.echo(f"Unable to bind to {DEFAULT_CLIENT_ADDRESS}:{DEFAULT_CLIENT_PORT}")
        click.echo(f"Trying {DEFAULT_CLIENT_ADDRESS}:{DEFAULT_CLIENT_PORT + 1}")
        sock.bind((DEFAULT_CLIENT_ADDRESS, DEFAULT_CLIENT_PORT + 1))

    sock.settimeout(timeout)
    return sock


# \\cheats\\0\\deathmatch\\1\\dmflags\\16\\fraglimit\\0\\gamedate\\Dec 23 2019\\gamename\\baseq2\\hostname\\noname\\mapname\\q2dm1\\maxclients\\8\\maxspectators\\4\\needpass\\0\\protocol\\34\\timelimit\\0\\version\\7.43pre x86_64 Dec 23 2019 Linux\n
def build_payload(
    header: bytes,
    data: Optional[tuple[tuple[str]]] = None,
) -> bytes:

    newline: bytes = CLIENT.newline.encode(CLIENT.encoding)
    string_data: str = CLIENT.split.join([CLIENT.split.join(datum) for datum in data])

    return newline.join([header, string_data.encode(CLIENT.encoding)])


def _generate_request(
    host: str = DEFAULT_HOST_ADDRESS,
    port: int = DEFAULT_HOST_PORT,
    request: str = DEFAULT_CHOICE,
    data: Optional[tuple[tuple[str]]] = None,
    timeout: float = DEFAULT_TIMEOUT,
    buffer: int = DEFAULT_BUFFER,
    wait_for_response: bool = False,
    quiet: bool = False,
) -> tuple[Optional[bytes], Optional[bytes]]:

    sock: socket.socket = _setup_socket(timeout, quiet)

    if not quiet:
        click.echo(f"Connecting to {host}:{port}...")
    header: BaseProtocolHeader = CLIENT.headers.get(request)

    payload: bytes = build_payload(header=header.received, data=data)
    sock.sendto(payload, (host, port))
    if not quiet:
        click.echo(f"Sent:       {payload!r}")

    request_response: Optional[bytes] = None
    if header.response and not quiet:
        click.echo(f"Expecting:  {header.response!r}")

    if header.response or wait_for_response:
        try:
            request_response = sock.recv(buffer)
        except TimeoutError:
            if not quiet:
                click.echo("Connection timed out waiting for response")
            return header.response, None
        else:
            if not quiet:
                click.echo(f"Received:   {request_response!r}")

    return header.response, request_response
