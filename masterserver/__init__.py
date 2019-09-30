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
    logging.debug(f"{__class__.__name__ } - Recieved {data} from {address[0]}:{address[1]}")
    headers, *status = data.splitlines()

    result = self.protocols.is_client(headers)
    if result:
      response = self.handle_client(result)
    else:
      result = self.protocols.is_server(headers)
      response = self.handle_server(result)

    if response:
      logging.debug(f"{__class__.__name__ } - Sending {response} to {address}")
      self.transport.sendto(response, address)

  def handle_client(self):
    logging.debug(f"{__class__.__name__ } - Header belongs to client")
    response_header = result.get('resp', None)
    server_list = self.storage.list_servers(result.get('game'))
    response = self.create_response(response_header, server_list)
    return response

  def handle_server(self):
    logging.debug(f"{__class__.__name__ } - Header belongs to server")
    server = GameServer(address, status, result.get('encoding'))
    if server.is_valid:
      if self.storage.get_server(server):
        self.storage.update_server(server)
      else:
        self.storage.create_server(server)

    if result.get('active', True) is False:
      self.storage.server_shutdown(server)

    response = result.get('resp', None)
    return response

  def create_response(self, header, response):
    # TODO: Clean up, add type conparison for if we ever need to return non-bytes (???)
    if header:
      x = [header]
      y = [_ for _ in response]

      return b'\n'.join(x + y)
    else:
      return response
