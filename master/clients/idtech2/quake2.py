#!/usr/bin/env python
import socket
from enum import Enum

import click

# from master.protocols.models.idtech2.quake2 import Quake2

DEFAULT_HOST: str = socket.gethostbyname(socket.gethostname())
DEFAULT_PORT: int = 27900


class Request(Enum):
    PING: bytes = b"\xff\xff\xff\xffping"
    STATUS: bytes = b"\xff\xff\xff\xffstatus"
    SHUTDOWN: bytes = b"\xff\xff\xff\xffshutdown"


@click.command()
@click.option("-h", "--host", "host", default=DEFAULT_HOST, type=str)
@click.option("-p", "--port", "port", default=DEFAULT_PORT, type=int)
@click.option(
    "-r",
    "--request",
    "request",
    type=click.Choice(["ping", "status", "shutdown"], case_sensitive=False),
    default="ping",
)
def main(
    host: str,
    port: int,
    request: str,
) -> None:

    message: bytes = getattr(Request, request.upper())
    sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(30.0)

    print(f"Connecting to {host}:{port}...")

    sock.sendto(message, (host, port))
    print(f"Sent:     {message!r}")

    received: bytes = sock.recv(1024)
    print(f"Received: {received!r}")


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
