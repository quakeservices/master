import logging
from datetime import datetime

from pynamodb.indexes import GlobalSecondaryIndex, AllProjection

from pynamodb.models import Model
from pynamodb.attributes import (
        UnicodeAttribute,
        UnicodeSetAttribute,
        NumberAttribute,
        UTCDateTimeAttribute,
        BooleanAttribute,
        JSONAttribute
)

class ServerIndex(GlobalSecondaryIndex):
  class Meta:
    read_capacity_units = 5
    write_capacity_units = 5
    index_name = 'server_index'
    projection = AllProjection()

  address = UnicodeAttribute(hash_key=True)
  port = NumberAttribute(range_key=True)

class Server(Model):
  class Meta:
    table_name = 'server'
    region = 'ap-southeast-2' # Note: Not needed in production
    read_capacity_units = 5
    write_capacity_units = 5

  server_index = ServerIndex()

  address = UnicodeAttribute(hash_key=True)
  port = NumberAttribute(range_key=True)

  status = JSONAttribute()

  players = UnicodeSetAttribute()

  active = BooleanAttribute(default=True)
  first_seen = UTCDateTimeAttribute(default=datetime.utcnow())
  last_seen = UTCDateTimeAttribute(default=datetime.utcnow())

  # country_short = UnicodeAttribute()
  # country_long = UnicodeAttribute()


class Storage(object):
  def __init__(self):
    logging.debug(f"{__class__.__name__ } - Initialising storage.")
    if not Server.exists():
      Server.create_table(wait=True)

  def get_server(self, server):
    logging.debug(f"{__class__.__name__ } - get_server {server.address}:{server.port}")
    for server in Server.server_index.query(address=server.address, port=server.port):
      logging.debug(f"{__class__.__name__ } - {server}")
      return True
    return False

  def list_servers(self, game):
    logging.debug(f"{__class__.__name__ } - list_servers for {game}")
    return Server.scan()

  def create_server(self, server):
    logging.debug(f"{__class__.__name__ } - create_server {server.address}:{server.port}")
    server_obj = Server(server.address, server.port, status=server.status)
    server_obj.save()

  def update_server(self, server):
    """
    TODO: Flesh this out so it actually updates a server
    """
    logging.debug(f"{__class__.__name__ } - update_server {server.address}:{server.port}")
    server_obj = Server(server.address, server.port, status=server.status)
    server_obj.save()
