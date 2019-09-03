import logging
import json

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

"""
TODO: Grab first_seen before it's overridden
"""


class ServerIndex(GlobalSecondaryIndex):
  class Meta:
    read_capacity_units = 5
    write_capacity_units = 5
    index_name = 'server_index'
    projection = AllProjection()

  address = UnicodeAttribute(hash_key=True)


class Server(Model):
  class Meta:
    table_name = 'server'
    region = 'ap-southeast-2' # Note: Not needed in production
    read_capacity_units = 5
    write_capacity_units = 5

  server_index = ServerIndex()

  address = UnicodeAttribute(hash_key=True)

  status = JSONAttribute()

  player_count = NumberAttribute(default=0)
  players = JSONAttribute()

  active = BooleanAttribute(default=True)
  scraped = BooleanAttribute(default=False) # Whether the server was scraped from other master servers

  first_seen = UTCDateTimeAttribute(default=datetime.utcnow())
  last_seen = UTCDateTimeAttribute(default=datetime.utcnow())

  country_code = UnicodeAttribute()


class Storage(object):
  def __init__(self):
    logging.debug(f"{__class__.__name__ } - Initialising storage.")
    self.create_table()

  def create_table(self):
    try:
      Server.create_table(wait=True)
    except:
      pass

  def new_server_object(self, server):
    return Server(server.address,
                  player_count=server.player_count,
                  country_code=server.country,
                  status=json.dumps(server.status),
                  players=json.dumps(server.players))

  def get_server(self, server):
    logging.debug(f"{__class__.__name__ } - get_server {server.address}")
    for server in Server.server_index.query(server.address):
      logging.debug(f"{__class__.__name__ } - {server}")
      return True
    return False

  def list_servers(self, game):
    logging.debug(f"{__class__.__name__ } - list_servers for {game}")
    return Server.scan()

  def create_server(self, server):
    logging.debug(f"{__class__.__name__ } - create_server {server.address}")
    server_obj = self.new_server_object(server)
    server_obj.save()

  def update_server(self, server):
    """
    TODO: Flesh this out so it actually updates a server
    """
    logging.debug(f"{__class__.__name__ } - update_server {server.address}")
    server_obj = self.new_server_object(server)
    server_obj.save()
