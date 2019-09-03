import logging

from gameserver import GameServer


class MasterServer:
  def __init__(self, storage, protocols):
    logging.debug(f"{__class__.__name__ } - Initialising master server.")
    self.storage = storage
    self.protocols = protocols

  def connection_made(self, transport):
    self.transport = transport

  def datagram_received(self, data, address):
    response = None
    if b'\n' in data:
      headers, *status = data.split(b'\n')
      logging.debug(f"{__class__.__name__ } - Recieved {headers} from {address[0]}:{address[1]}")
    else:
      headers = data

    result = self.protocols.is_client(headers)
    if result:
      logging.debug(f"{__class__.__name__ } - Header belongs to client")
      response_header = result.get('resp', None)
      response = self.create_response(response_header, self.storage.list_servers(result.get('game')))
    else:
      result = self.protocols.is_server(headers)
      if result:
        server = GameServer(address, status, result.get('encoding', 'latin1'))
        logging.debug(f"{__class__.__name__ } - Header belongs to server")
        if server.is_valid:
          if self.storage.get_server(server):
            self.storage.update_server(server)
          else:
            self.storage.create_server(server)

        if result.get('active', True) is False:
          self.storage.server_shutdown(server)

        response = result.get('resp', None)

    if response:
      self.transport.sendto(response, address)

  def create_response(self, header, response):
    # TODO: Clean up, add type conparison for if we ever need to return non-bytes (???)
    if header:
      x = [header]
      y = [_ for _ in response]

      return b'\n'.join(x + y)
    else:
      return response
