from datetime import datetime

from storage import BaseStorage
from storage.models.pynamodb import PynamoServer


# TODO: This a hot mess in need of a rework
#       or alternatively removal
class PynamoDbStorage(BaseStorage):
    def server_object(self, server):
        return PynamoServer(
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
        for server in PynamoServer.server_index.query(server.address, limit=1):
            return server

    def get_server(self, server):
        query = self.get_server_obj(server)
        if query:
            return True
        else:
            return False

    def list_servers(self, game=None):
        servers = [server for server in PynamoServer.scan() if server.active]

        return servers

    def list_server_addresses(self, game=None):
        servers = [server.address for server in self.list_servers()]

        return servers

    def save_server(self, server):
        if self.get_server(server):
            self._update_server(server)
        else:
            self._create_server(server)

    def _create_server(self, server):
        try:
            server_obj = self.server_object(server)
            server_obj.save()
        except ValueError:
            raise

    def _update_server(self, server):
        try:
            server_obj = self.get_server_obj(server)
            server_obj.update(
                actions=[
                    PynamoServer.active.set(True),
                    PynamoServer.game.set(server.game),
                    PynamoServer.last_seen.set(datetime.utcnow()),
                    PynamoServer.status.set(server.status),
                    PynamoServer.players.set(server.players),
                    PynamoServer.player_count.set(server.player_count),
                ]
            )
        except ValueError:
            raise

    def server_shutdown(self, server):
        try:
            server_obj = self.get_server_obj(server)
            server_obj.update(
                actions=[
                    PynamoServer.active.set(False),
                    PynamoServer.last_seen.set(datetime.utcnow()),
                ]
            )
        except ValueError:
            raise