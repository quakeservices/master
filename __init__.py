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
        if not os.getenv('SKIP_TABLE_CREATE', 'True'):
            logging.debug(f"{self.__class__.__name__ } - Creating table...")
            self.create_table()
            logging.debug(f"{self.__class__.__name__ } - Table created.")
        else:
            logging.debug(f"{self.__class__.__name__ } - Skipping table creation.")

    @staticmethod
    def create_table():
        try:
            Server.create_table(wait=True)
        except:
            raise

    @staticmethod
    def server_object(server):
        """
        TODO: Grab first_seen before it's overridden
                    Update active
        """
        return Server(server.address,
                      country_code=server.country,
                      active=server.active,
                      status=server.status,
                      players=server.players,
                      player_count=server.player_count)

    @staticmethod
    def get_server(server):
        return Server(server.address).exists()

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
        """
        TODO: Flesh this out so it actually updates a server
        """
        logging.debug(f"{self.__class__.__name__ } - update_server {server.address}")
        try:
            server_obj = self.server_object(server)
            server_obj.active = True
            server_obj.save()
        except:
            logging.debug(f"{self.__class__.__name__ } - failed for some reason {server.address}")

    def server_shutdown(self, server):
        """
        TODO: Flesh this out so it actually updates a server
        """
        logging.debug(f"{self.__class__.__name__ } - update_server {server.address}")
        self.cache.invalidate('servers')
        server_obj = self.server_object(server)
        server_obj.active = False
        server_obj.save()
