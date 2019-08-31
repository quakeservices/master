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
      headers, *server_status = data.split(b'\n')
      logging.debug(f"{__class__.__name__ } - Recieved {headers} from {address[0]}:{address[1]}")
    else:
      logging.debug(f"{__class__.__name__ } - Recieved {data}")
      return b'Hi'


    result = self.protocols.is_client(headers)
    if result:
      logging.debug(f"{__class__.__name__ } - Header belongs to client")
      response = self.create_response(result, self.storage.list_servers)
    else:
      result = self.protocols.is_server(headers)
      if result:
        server = GameServer(address, server_status)
        logging.debug(f"{__class__.__name__ } - Header belongs to server")
        if server.is_valid:
          if self.storage.get_server(server):
            self.storage.update_server(server)
          else:
            self.storage.create_server(server)

          response = result.get('resp', None)

    if response:
      self.transport.sendto(response, address)

  def create_reponse(self, protocol, response):
    # TODO: Clean up, add type conparison for if we ever need to return non-bytes (???)
    if protocol[1].get('resp', None):
      return b'\n'.join(protocol[1].get('resp'), response)
    else:
      return response
