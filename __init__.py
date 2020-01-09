from datetime import datetime, timedelta

import logging
import os
import json
import pickle

from .model import Server
from .cache import Cache


class Storage():
    def __init__(self):
        logging.debug(f"{self.__class__.__name__ } - Initialising storage.")
        self.cache = Cache()
        logging.debug(f"{self.__class__.__name__ } - Creating table...")
        self.create_table()
        logging.debug(f"{self.__class__.__name__ } - Table created.")

    @staticmethod
    def create_table():
        try:
            Server.create_table(wait=True)
        except:
            raise

    @staticmethod
    def server_object(server):
        return Server(server.address,
                      country_code=server.country,
                      active=True,
                      status=server.status,
                      players=server.players,
                      player_count=server.player_count)

    def get_server(self, server):
        logging.debug(f"{self.__class__.__name__ } - looking for {server.address}")

        query = Server.server_index.query(server.address, limit=1)
        result = False

        for item in query:
            logging.debug(f"{self.__class__.__name__ } - found {item}")
            result = True

        return result

    @staticmethod
    def get_server_obj(server):
        """
        Replace with this?
        server = None
        try:
            server = Server.server_index.query(server.address).__next__()
        except StopIteration:
            pass
        finally:
            return Server
        """
        return Server.get(server.address)

    def list_servers(self, game):
        logging.debug(f"{self.__class__.__name__ } - list_servers for {game}")
        servers = self.cache.get(f'servers')
        if not servers:
            servers = [_.address.encode('latin1') for _ in Server.scan()]
            self.cache.set('servers', servers)

        return servers

    def create_server(self, server):
        logging.debug(f"{self.__class__.__name__ } - create_server {server.address}")
        self.cache.invalidate('servers')
        try:
            server_obj = self.server_object(server)
            server_obj.save()
        except:
            logging.debug(f"{self.__class__.__name__ } - failed for some reason {server.address}")

    def update_server(self, server):
        logging.debug(f"{self.__class__.__name__ } - update_server {server.address}")
        try:
            server_obj = self.get_server_obj(server)
            server_obj.update(actions=[
              Server.active.set(True),
              Server.last_seen.set(datetime.utcnow()),
              Server.status.set(server.status),
              Server.players.set(server.players),
              Server.player_count.set(server.player_count)
            ])
        except:
            logging.debug(f"{self.__class__.__name__ } - failed for some reason {server.address}")

    def server_shutdown(self, server):
        logging.debug(f"{self.__class__.__name__ } - update_server {server.address}")
        self.cache.invalidate('servers')
        try:
            server_obj = self.get_server_obj(server)
            server_obj.update(actions=[
              Server.active.set(False),
              Server.last_seen.set(datetime.utcnow())
            ])
        except:
            logging.debug(f"{self.__class__.__name__ } - failed for some reason {server.address}")
