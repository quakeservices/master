from headers import Headers

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


class Socket(object):
    pass


class MockTransport(object):
    pass
