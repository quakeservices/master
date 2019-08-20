import logging

from pynamodb.models import Model
from pynamodb.attributes import (
        UnicodeAttribute,
        UnicodeSetAttribute,
        NumberAttribute,
        UTCDateTimeAttribute,
        BooleanAttribute
)


class Server(Model):
  class Meta:
    table_name = 'server'

  address = UnicodeAttribute(hash_key=True)
  port = NumberAttribute(range_key=True)

  game = UnicodeAttribute()
  name = UnicodeAttribute()
  map = UnicodeAttribute()

  players = UnicodeSetAttribute()

  active = BooleanAttribute()
  first_seen = UTCDateTimeAttribute(default=datetime.utcname())
  last_seen = UTCDateTimeAttribute(default=datetime.utcname())

  country_short = UnicodeAttribute()
  country_long = UnicodeAttribute()


class Storage(object):
  def __init__(self):
    logging.debug(f"{__class__.__name__ } - Initialising storage.")
    self.client = boto3.resource('dynamodb')
    self.table = self.client.Table('master')

  def get_server(self, server):
    """
    https://pynamodb.readthedocs.io/en/latest/api.html#pynamodb.models.Model.get
    """
    logging.debug(f"{__class__.__name__ } - get_server {server.address}:{server.port}")
    return Server.get(server.address, server.port)

  def list_servers(self, game):
    """
    https://pynamodb.readthedocs.io/en/latest/api.html#pynamodb.models.Model.scan
    """
    logging.debug(f"{__class__.__name__ } - list_servers for {game}")
    return Server.scan()

  def create_server(self, server):
    """
    https://pynamodb.readthedocs.io/en/latest/api.html#pynamodb.models.Model.save
    """
    logging.debug(f"{__class__.__name__ } - create_server {server.address}:{server.port}")
    server_obj = Server(server)

    try:
      server_obj.save()
    except:
      return False
    else:
      return True

  def update_server(self, server):
    """
    TODO: Flesh this out so it actually updates a server
    """
    logging.debug(f"{__class__.__name__ } - update_server {server.address}:{server.port}")
    server_obj = Server.get(server.address, server.port)
    server_obj = server

    try:
      server_obj.save()
    except:
      return False
    else:
      return True
