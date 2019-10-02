import logging
import os
import json
import redis
import pickle

from datetime import datetime, timedelta

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
    if os.getenv('STAGE', 'PRODUCTION') == 'TESTING':
      host = 'http://dynamodb:8000'
    read_capacity_units = 5
    write_capacity_units = 5
    index_name = 'server_index'
    projection = AllProjection()

  address = UnicodeAttribute(hash_key=True)


class Server(Model):
  class Meta:
    if os.getenv('STAGE', 'PRODUCTION') == 'TESTING':
      host = 'http://dynamodb:8000'
    table_name = 'server'
    read_capacity_units = 5
    write_capacity_units = 5

  server_index = ServerIndex()

  address = UnicodeAttribute(hash_key=True)

  protocol = NumberAttribute(default=0)

  status = JSONAttribute()

  player_count = NumberAttribute(default=0)
  players = JSONAttribute()

  active = BooleanAttribute(default=True)
  scraped = BooleanAttribute(default=False) # Whether the server was scraped from other master servers

  first_seen = UTCDateTimeAttribute(default=datetime.utcnow())
  last_seen = UTCDateTimeAttribute(default=datetime.utcnow())

  country_code = UnicodeAttribute(default='ZZ')


class Storage(object):
  def __init__(self):
    logging.debug(f"{__class__.__name__ } - Initialising storage.")
    self.cache = Cache()
    self.create_table()

  def create_table(self):
    try:
      logging.debug(f"{__class__.__name__ } - Creating table...")
      Server.create_table(wait=True)
    except:
      logging.debug(f"{__class__.__name__ } - Failed to create table.")
      raise
    else:
      logging.debug(f"{__class__.__name__ } - Table created.")

  def server_object(self, server):
    """
    TODO: Grab first_seen before it's overridden
          Update active
    """
    return Server(server.address,
                  country_code=server.country,
                  status=server.status,
                  players=server.players,
                  player_count=server.player_count)

  def get_server(self, server):
    return Server(server.address).exists()

  def list_servers(self, game):
    logging.debug(f"{__class__.__name__ } - list_servers for {game}")
    servers = self.cache.get(f'{game}_servers')
    if not servers:
      servers = [_.address.encode('latin1') for _ in Server.scan()]
      self.cache.set('servers', servers)

    return servers

  def create_server(self, server):
    logging.debug(f"{__class__.__name__ } - create_server {server.address}")
    self.cache.invalidate(f'{server.game}_servers')
    try:
      server_obj = self.server_object(server)
      server_obj.save()
    except:
      logging.debug(f"{__class__.__name__ } - failed for some reason {server.address}")
      pass

  def update_server(self, server):
    """
    TODO: Flesh this out so it actually updates a server
    """
    logging.debug(f"{__class__.__name__ } - update_server {server.address}")
    try:
        server_obj = self.server_object(server)
        server_obj.active = True
        server_obj.save()
    except:
      logging.debug(f"{__class__.__name__ } - failed for some reason {server.address}")
      pass

  def server_shutdown(self, server):
    """
    TODO: Flesh this out so it actually updates a server
    """
    logging.debug(f"{__class__.__name__ } - update_server {server.address}")
    self.cache.invalidate(f'{server.game}_servers')
    server_obj = self.server_object(server)
    server_obj.active = False
    server_obj.save()


class Cache(object):
  def __init__(self):
    logging.debug(f"{__class__.__name__ } - Initialising cache.")
    self.redis = redis.Redis(host='redis',
                             port=6379,
                             db=0,
                             socket_timeout=3,
                             socket_connect_timeout=5,
                             socket_keepalive=True)

  def get(self, key):
    value = self.redis.get(key)
    if value:
      try:
        result = pickle.loads(value)
      except KeyError:
        logging.debug(f"{__class__.__name__ } - key error: possibly unpickled object?")
        result = value
      else:
        return result
    else:
      return False

  def set(self, key, value):
    logging.debug(f"{__class__.__name__ } - caching {value} as {key}.")
    value = picke.dumps(value)
    try:
      self.redis.setex(key, timedelta(hours=1),value)
    except:
      return False
    else:
      return True

  def invalidate(self, key):
    logging.debug(f"{__class__.__name__ } - forcing {key} to expire.")
    self.redis.expire(key, 0)
