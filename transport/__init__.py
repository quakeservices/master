import asyncio
import socket
import signal
import functools
import logging


class Transport():
    def __init__(self, master):
        logging.debug(f"{self.__class__.__name__ } - Initialising transport")
        self.master = master
        self.loop = asyncio.get_event_loop()
        self.signal()
        self.v4_udp_transport, self.v4_udp_protocol = self.listener(ipv=4)
        self.v6_udp_transport, self.v6_udp_protocol = self.listener(ipv=6)

    def signal(self):
        logging.debug(f"{self.__class__.__name__ } - Setting up signals")
        signals = ('SIGINT', 'SIGTERM')
        for signame in signals:
            self.loop.add_signal_handler(getattr(signal, signame),
                                         functools.partial(self.shutdown, signame))

    def listener(self, ipv=4):
        if ipv == 6:
            logging.debug(f"{self.__class__.__name__ } - Setting up IPv6 listener")
            socket_family = socket.AF_INET6
            bind = ('::', 27900)
        else:
            logging.debug(f"{self.__class__.__name__ } - Setting up IPv4 listener")
            socket_family = socket.AF_INET
            bind = ('0.0.0.0', 27900)

        listen = self.loop.create_datagram_endpoint(lambda: self.master,
                                                    family=socket_family,
                                                    local_addr=bind)

        transport, protocol = self.loop.run_until_complete(listen)

        return transport, protocol

    def shutdown(self, sig):
        logging.debug(f"{self.__class__.__name__ } - Caught {sig}")
        if self.v4_udp_transport:
            logging.debug(f"{self.__class__.__name__ } - Closing IPv4 transport")
            self.v4_udp_transport.close()

        if self.v6_udp_transport:
            logging.debug(f"{self.__class__.__name__ } - Closing IPv6 transport")
            self.v6_udp_transport.close()
        self.loop.stop()
