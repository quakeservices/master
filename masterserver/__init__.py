from gameserver import GameServer


class MasterServer(object):
    def __init__(self, storage, transport, headers):
        self.storage = storage
        self.transport = transport
        self.headers = headers
        
        if self.transport.has_loop:
            self.transport.start_loop()
