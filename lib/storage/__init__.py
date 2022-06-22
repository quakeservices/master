from dataclasses import dataclass
from typing import Optional, Union

from helper import LoggingMixin


@dataclass
class Server:
    # TODO: Replace GameServer class with this
    active: bool
    game: str
    details: dict[str, Union[str, int]]
    players: list[dict[str, str]]

    server_address: Optional[str] = None
    server_ip: Optional[str] = None
    server_port: Optional[int] = None

    def __post_init__(self):
        self._validate_server_address()

    def _validate_server_address(self):
        if self.server_address:
            server_ip, server_port = self.server_address.split(":")
            self.server_ip = server_ip
            self.server_port = int(server_port)
        elif self.server_ip and self.server_port:
            self.server_address = ":".join([self.server_ip, str(self.server_port)])
        else:
            raise ValueError(
                "Either server_address, or both server_ip and server_port must be set"
            )


class BaseStorage(LoggingMixin):
    def create_server(self, server_data: Server) -> bool:
        """
        Return True on successful create
        Return Fale on failed create
        """
        raise NotImplementedError

    def get_server(
        self, server_address: str, game: Optional[str] = None
    ) -> Optional[Server]:
        """
        Return optional Server object
        """
        raise NotImplementedError

    def get_servers(self, game: Optional[str] = None) -> list[Server]:
        """
        Return a list of Server objects
        """
        raise NotImplementedError

    def update_server(self, server_data: Server) -> bool:
        """
        Return True on successful update
        Return Fale on failed update
        """
        raise NotImplementedError
