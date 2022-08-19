from master.protocols.models import BaseProtocolHeader, Headers
from master.protocols.models.idtech1 import Idtech1Protocol


class QuakeWorld(Idtech1Protocol):
    game: str = "quakeworld"
    active: bool = False
    versions: list[str] = ["28"]
    headers: Headers = {
        "ping": BaseProtocolHeader(
            received=b"k",
            response=b"l",
            header_type="any",
        ),
        "heartbeat": BaseProtocolHeader(
            received=b"a",
            response=b"l",
            header_type="server",
        ),
        "shutdown": BaseProtocolHeader(received=b"C", header_type="server"),
        "query": BaseProtocolHeader(received=b"c", response=b"d", header_type="client"),
    }
