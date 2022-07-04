#!/usr/bin/env python
import socket
from typing import Optional


def main(
    host: Optional[str] = None,
    port: Optional[int] = 27900,
    message: Optional[bytes] = None,
):
    if not host:
        host = socket.gethostbyname(socket.gethostname())
    if not message:
        message = b"\xff\xff\xff\xffping"

    sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message, (host, port))

    received: bytes = sock.recv(1024)

    print(f"Sent:     {message!r}")
    print(f"Received: {received!r}")


if __name__ == "__main__":
    main()
