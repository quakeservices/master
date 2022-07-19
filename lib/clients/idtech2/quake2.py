#!/usr/bin/env python
import socket
from enum import Enum
from typing import Optional

import click

# https://click.palletsprojects.com/en/8.1.x/options/#boolean-flags

DEFAULT_HOST = socket.gethostbyname(socket.gethostname())


class Request(Enum):
    PING: bytes = b"\xff\xff\xff\xffping"
    STATUS: bytes = b"\xff\xff\xff\xffstatus"
    SHUTDOWN: bytes = b"\xff\xff\xff\xffshutdown"


@click.command()
@click.option("-h", "--host", "host", default=DEFAULT_HOST, type=str)
@click.option("-p", "--port", "port", default=27900, type=int)
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

    sock.sendto(message.value, (host, port))
    print(f"Sent:     {message.value!r}")

    received: bytes = sock.recv(1024)
    print(f"Received: {received!r}")


if __name__ == "__main__":
    main()
