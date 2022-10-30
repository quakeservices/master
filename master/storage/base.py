from master.storage.models.server import Server


class BaseStorage:
    def __init__(self) -> None:
        pass

    @classmethod
    def initialise(cls) -> None:
        """
        Initialise the storage backend.
        Creating tables for example.
        """
        raise NotImplementedError

    def create_server(self, server: Server) -> bool:
        """
        Return True on successful create
        Return Fale on failed create
        """
        raise NotImplementedError

    def get_server(self, address: str, game: str | None = None) -> Server | None:
        """
        Return optional Server object
        """
        raise NotImplementedError

    def get_servers(self, game: str | None = None) -> list[Server]:
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
