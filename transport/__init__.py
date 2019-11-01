import asyncio
import socket
import signal
import functools
import logging


class Transport():
    def __init__(self, master):
        logging.debug(f"{self.__class__.__name__ } - Initialising transport")
        self.loop = asyncio.get_event_loop()
        self.signal()
        self.v4_udp_transport, self.v4_udp_protocol = self.listener(master,
                                                                    socket.AF_INET,
                                                                    ('0.0.0.0', 27900))
        self.v6_udp_transport, self.v6_udp_protocol = self.listener(master,
                                                                    socket.AF_INET6,
                                                                    ('::', 27900))

    def signal(self):
        logging.debug(f"{self.__class__.__name__ } - Setting up signals")
        signals = ('SIGINT', 'SIGTERM')
        for signame in signals:
            self.loop.add_signal_handler(getattr(signal, signame),
                                         functools.partial(self.shutdown, signame))

    def listener(self, server, socket_family, bind):
        logging.debug(f"{self.__class__.__name__ } - Setting up listener on {bind}")

        listen = self.loop.create_datagram_endpoint(lambda: server,
                                                    family=socket_family,
                                                    local_addr=bind)

        transport, protocol = self.loop.run_until_complete(listen)

        return transport, protocol

    def shutdown(self, sig):
        logging.debug(f"{self.__class__.__name__ } - Caught {sig}")
        if self.v4_udp_transport:
            logging.debug(f"{self.__class__.__name__ } - Closing IPv4 UDP transport")
            self.v4_udp_transport.close()

        if self.v6_udp_transport:
            logging.debug(f"{self.__class__.__name__ } - Closing IPv6 UDP transport")
            self.v6_udp_transport.close()
        self.loop.stop()


class HealthCheck(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport #pylint: disable=attribute-defined-outside-init

    def data_received(self, data):
        self.transport.write(b'HTTP/1.1 200 Success\n')
        self.transport.close()
