import socket
from random import choice
from typing import Optional, Union

from master.constants import (
    DEFAULT_BUFFER,
    DEFAULT_CLIENT_ADDRESS,
    DEFAULT_CLIENT_PORT,
    DEFAULT_HOST_ADDRESS,
    DEFAULT_HOST_PORT,
    DEFAULT_TIMEOUT,
)
from master.protocols.encoder import Encoder
from master.protocols.models import BaseProtocolHeader
from master.protocols.models.game import GameProtocol

Details = Union[dict, tuple[tuple[str, str]]]
Players = Union[list[dict[str, str]], tuple[tuple[str, str, str]]]


def _setup_socket(
    client_host: str,
    client_port: int,
    timeout: float,
    quiet: bool,
    bail_on_failure: bool = False,
) -> Optional[socket.socket]:
    sock: Optional[socket.socket] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    if not quiet:
        print(f"Binding client to {client_host}:{client_port}... ", end="")

    try:
        sock.bind((client_host, client_port))
    except OSError:
        if not quiet:
            print(f"Unable to bind to {client_host}:{client_port}")

        if client_port != DEFAULT_CLIENT_PORT:
            sock = _setup_socket(client_host, DEFAULT_CLIENT_PORT, timeout, quiet)
        elif not bail_on_failure:
            sock = _setup_socket(
                client_host, client_port + 1, timeout, quiet, bail_on_failure=True
            )
    else:
        if not quiet:
            print("Binding successful.")

    sock.settimeout(timeout)
    return sock


def _send_payload(
    sock: socket.socket,
    host: str,
    port: int,
    payload: bytes,
    quiet: bool,
    dry_run: bool,
) -> None:
    """
    Resolve 'host' to an IP address and send payload to socket
    """
    address_info = socket.getaddrinfo(host, port)
    addresses: list[tuple] = [
        info for info in address_info if info[1] == socket.SOCK_DGRAM
    ]
    address: tuple[str, int] = choice(addresses)[4]

    if not quiet:
        if host != address[0]:
            print(f"{host} resolved to {address[0]}... ", end="")
        print(f"Sending payload to {address[0]}:{address[1]}.")

    if not dry_run:
        sock.sendto(payload, address)

    if not quiet:
        print(f"Sent:       {payload!r}")


def _create_payload(
    protocol: GameProtocol,
    request: str,
    details: Optional[Details] = None,
    players: Optional[Players] = None,
) -> bytes:
    if isinstance(details, tuple):
        _details: dict = dict(details)
    if isinstance(players, tuple):
        _players: list[dict[str, str]] = [
            {"score": player[0], "ping": player[1], "name": player[2]}
            for player in players
        ]

    encoder = Encoder(protocol)
    return encoder.encode(request, details=_details, players=_players)


# pylint: disable=too-many-locals
def _generate_request(
    protocol: GameProtocol,
    request: str,
    host: str = DEFAULT_HOST_ADDRESS,
    port: int = DEFAULT_HOST_PORT,
    client_host: str = DEFAULT_CLIENT_ADDRESS,
    client_port: int = DEFAULT_CLIENT_PORT,
    details: Optional[Details] = None,
    players: Optional[Players] = None,
    timeout: float = DEFAULT_TIMEOUT,
    buffer: int = DEFAULT_BUFFER,
    wait_for_response: bool = False,
    quiet: bool = False,
    dry_run: bool = False,
) -> tuple[Optional[bytes], Optional[bytes]]:
    """
    Given a GameProtocol send a request to a master server
    Returns a tuple of:
        Expected response   [Optional bytes]
        Actual response     [Optional bytes]
    """

    sock: Optional[socket.socket] = _setup_socket(
        client_host, client_port, timeout, quiet
    )
    if not sock:
        return None, None

    header: BaseProtocolHeader = protocol.headers.get(request)
    payload: bytes = _create_payload(protocol, request, details, players)
    _send_payload(
        sock=sock, host=host, port=port, payload=payload, quiet=quiet, dry_run=dry_run
    )

    request_response: Optional[bytes] = None
    if header.response and not quiet:
        print(f"Expecting:  {header.response!r}")

    if not dry_run and (header.response or wait_for_response):
        try:
            request_response = sock.recv(buffer)
        except TimeoutError:
            if not quiet:
                print("Connection timed out waiting for response")
            return header.response, None
        else:
            if not quiet:
                print(f"Received:   {request_response!r}")

    return header.response, request_response
