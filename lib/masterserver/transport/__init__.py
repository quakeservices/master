import asyncio
import enum
import functools
import logging
import signal
import socket
from typing import Callable, Literal, Optional

from masterserver import MasterServer


class Transport(asyncio.Protocol):
    loop: asyncio.AbstractEventLoop
    port: int = 27900
    v4_bind: str = "0.0.0.0"
    v4_enabled: bool = True
    v4_udp_protocol: Optional[asyncio.DatagramProtocol] = None
    v4_udp_transport: Optional[asyncio.DatagramTransport] = None
    v6_bind: str = "::"
    v6_enabled: bool = False
    v6_udp_protocol: Optional[asyncio.DatagramProtocol] = None
    v6_udp_transport: Optional[asyncio.DatagramTransport] = None

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        master: MasterServer,
    ):
        self.loop = loop
        self.main(master)

    def main(self, master: MasterServer):
        logging.debug(f"{self.__class__.__name__ } - Initialising transport")

        self.signal()

        self.healt_check_transport = self.health_check(HealthCheck())

        if self.v4_enabled:
            self.v4_udp_transport, self.v4_udp_protocol = self._create_listener(
                lambda: master, socket.AF_INET, (self.v4_bind, self.port)
            )

        if self.v6_enabled:
            self.v6_udp_transport, self.v6_udp_protocol = self._create_listener(
                lambda: master, socket.AF_INET6, (self.v6_bind, self.port)
            )

    def signal(self):
        logging.debug(f"{self.__class__.__name__ } - Setting up signals")
        signals = ("SIGINT", "SIGTERM")
        for signame in signals:
            self.loop.add_signal_handler(
                getattr(signal, signame), functools.partial(self.shutdown, signame)
            )

    def _create_listener(
        self,
        server: Callable,
        socket_family: enum.IntEnum,
        bind: tuple[str, int],
    ) -> tuple[asyncio.DatagramTransport, asyncio.DatagramProtocol]:
        logging.debug(
            f"{self.__class__.__name__ } - Setting up master listener on {bind[0]}:{bind[1]}"
        )
        transport: asyncio.DatagramTransport
        protocol: asyncio.DatagramProtocol

        listener = self.loop.create_datagram_endpoint(
            server, family=socket_family, local_addr=bind
        )
        transport, protocol = self.loop.run_until_complete(listener)

        return transport, protocol

    def health_check(
        self,
        server: asyncio.Protocol,
        socket_family=socket.AF_INET,
        host: str = "0.0.0.0",
        port: int = 8080,
    ):

        logging.debug(
            f"{self.__class__.__name__ } - Setting up health check listener on {host}:{port}"
        )
        listen = self.loop.create_server(
            lambda: server, family=socket_family, host=host, port=port
        )
        transport = self.loop.run_until_complete(listen)

        return transport

    def shutdown(self, sig):
        logging.debug(f"{self.__class__.__name__ } - Caught {sig}")
        if self.healt_check_transport:
            logging.debug(f"{self.__class__.__name__ } - Closing health check listener")
            self.healt_check_transport.close()

        if self.v4_udp_transport:
            logging.debug(f"{self.__class__.__name__ } - Closing IPv4 UDP transport")
            self.v4_udp_transport.close()

        if self.v6_udp_transport:
            logging.debug(f"{self.__class__.__name__ } - Closing IPv6 UDP transport")
            self.v6_udp_transport.close()
        self.loop.stop()


class HealthCheck(asyncio.Protocol):
    transport = None

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data: bytes):
        logging.debug(f"{self.__class__.__name__ } - Received health check ping")
        self.transport.write(b"HTTP/1.1 200 Success\n")
