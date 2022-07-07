from typing import Optional, Union

from storage.models.server import Server


class BaseStorage:
    def create_server(self, server: Server) -> bool:
        """
        Return True on successful create
        Return Fale on failed create
        """
        raise NotImplementedError

    def get_server(self, address: str, game: Optional[str] = None) -> Optional[Server]:
        """
        Return optional Server object
        """
        raise NotImplementedError

    def get_servers(self, game: Optional[str] = None) -> list[Server]:
        """
        Return a list of Server objects
        """
        raise NotImplementedError

    def update_server(self, server: Server) -> bool:
        """
        Return True on successful update
        Return Fale on failed update
        """
        raise NotImplementedError
