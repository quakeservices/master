import logging

from gameserver import GameServer


class MasterServer:
  def __init__(self, storage, headers):
    logging.debug(f"{__class__.__name__ } - Initialising master server.")
    self.storage = storage
    self.headers = headers

  def connection_made(self, transport):
    self.transport = transport

  def datagram_received(self, data, address):
    response = None
    packet_headers, server_status = data.split(b'\n')

    result = self.headers.is_client(packet_headers)
    if result:
      response = self.create_response(result, storage.list_servers)
    
    # TODO: Why would this work?
    #       Fix this - it's a mess
    result = self.headers.is_server(packet_headers)
    if result:
      server = GameServer(self.headers, address, server_status)
      if server.is_valid:
        if storage.get_server(server):
          storage.update_server(server)
        else:
          storage.create_server(server)

        if server.has_response:
          response = server.response
    else:
      pass

    if response:
      self.transport.sendto(response, address)

  def create_reponse(self, header, response):
    # TODO: Clean up, add type conparison for if we ever need to return non-bytes (???)
    if header[1].get('resp', None):
      return b'\n'.join(header[1].get('resp'), response)
    else:
      return response
