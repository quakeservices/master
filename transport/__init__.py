import asyncio
import signal
import functools

class Transport(object):
    def __new__(self, backend):
        if backend is 'http':
            return HTTP()
        elif backend is 'socket':
            return Socket()
        else:
            return MockTransport()


class HTTP(object):
    def send(self, my_object):
        print(my_object)


def async_loop(f):
    loop = asyncio.get_event_loop()
    def decorated(*args, **kwargs):
        loop.run_until_complete(f(*args, **kwargs))
    return decorated

class Socket(object):
    def __init__(self, server, bind_address='127.0.0.1', bind_port=29700):
        self.bind_address = bind_address
        self.bind_port = bind_port
        self.bind = (self.bind_address, self.bind_port)
        self.loop = self.create_loop()
        self.listener = self.loop.create_datagram_endpoint(server,
                                                           local_addr=self.bind)

    def create_loop():
        loop = asyncio.get_event_loop()
        for signame in ('SIGINT', 'SIGTERM'):
            loop.add_signal_handler(getattr(signal, signame),
                                    functools.partial(shutdown, signame))
        return loop

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, address):
        # Do something with data...
        # Then reply
        self.transport.sendto(data, address)

    @property
    def has_loop(self):
        return True


class MockTransport(object):
    pass
