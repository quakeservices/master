from datetime import datetime

import logging
import os
import json
import pickle

from .model import Server


class Storage:
    def __init__(self):
        logging.debug(f"{self.__class__.__name__ } - Initialising storage.")

    @staticmethod
    def create_table():
        try:
            Server.create_table(wait=True)
        except:
            raise

    @staticmethod
    def server_object(server):
        logging.debug(
            f"{__class__.__name__ } - creating server for {server.address}"
        )  # pylint: disable=undefined-variable
        return Server(
            server.address,
            game=server.game,
            country_code=server.country,
            active=True,
            status=server.status,
            players=server.players,
            player_count=server.player_count,
        )

    @staticmethod
    def get_server_obj(server):
        for server in Server.server_index.query(server.address, limit=1):
            return server

    def get_server(self, server):
        logging.debug(f"{self.__class__.__name__ } - looking for {server.address}")

        query = self.get_server_obj(server)
        if query:
            return True
        else:
            return False

    def list_servers(self, game=None):
        logging.debug(f"{self.__class__.__name__ } - list_servers for {game}")
        servers = [server for server in Server.scan() if server.active]

        return servers

    def list_server_addresses(self, game=None):
        logging.debug(f"{self.__class__.__name__ } - list_servers for {game}")
        servers = [server.address for server in self.list_servers()]

        return servers

    def create_server(self, server):
        logging.debug(f"{self.__class__.__name__ } - create_server {server.address}")
        try:
            server_obj = self.server_object(server)
            server_obj.save()
        except ValueError:
            raise

    def update_server(self, server):
        logging.debug(f"{self.__class__.__name__ } - update_server {server.address}")
        try:
            server_obj = self.get_server_obj(server)
            server_obj.update(
                actions=[
                    Server.active.set(True),
                    Server.game.set(server.game),
                    Server.last_seen.set(datetime.utcnow()),
                    Server.status.set(server.status),
                    Server.players.set(server.players),
                    Server.player_count.set(server.player_count),
                ]
            )
        except ValueError:
            raise

    def server_shutdown(self, server):
        logging.debug(f"{self.__class__.__name__ } - update_server {server.address}")
        try:
            server_obj = self.get_server_obj(server)
            server_obj.update(
                actions=[
                    Server.active.set(False),
                    Server.last_seen.set(datetime.utcnow()),
                ]
            )
        except ValueError:
            raise
