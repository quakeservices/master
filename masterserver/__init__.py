from gameserver import GameServer


class MasterServer(object):
  def __init__(self, storage, transport, headers):
    self.storage = storage
    self.transport = transport
    self.headers = headers

  def connection_made(self, transport):
    self.conn = transport

  def datagram_received(self, data, address):
    response = None
    packet_headers, server_status = data.split(b'\n')

    if self.headers.is_client(packet_headers):
      response = storage.list_servers
    elif self.headers.is_server(packet_headers):
      server = GameServer(self.headers, address, server_status)
      if server.is_valid:
        storage.store(server)

        if server.has_response:
          response = server.response
    else:
      pass

    if response:
      self.conn.sendto(response, address)
