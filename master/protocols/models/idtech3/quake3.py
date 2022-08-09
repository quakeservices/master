from master.protocols.models import BaseProtocolHeader, Headers
from master.protocols.models.idtech3 import Idtech3Protocol


class Quake3(Idtech3Protocol):
    game: str = "quake3"
    active: bool = False
    versions: list[str] = ["68"]
    headers: Headers = {
        "ping": BaseProtocolHeader(
            received=b"\xff\xff\xff\xffping",
            response=b"\xff\xff\xff\xffack",
            header_type="any",
        ),
        "heartbeat": BaseProtocolHeader(
            received=b"\xff\xff\xff\xffheartbeat",  # TODO: Verify
            response=b"\xff\xff\xff\xffack",
            header_type="server",
        ),
        "shutdown": BaseProtocolHeader(
            received=b"\xff\xff\xff\xffshutdown", header_type="server"
        ),
        "query": BaseProtocolHeader(
            received=b"query", response=b"\xff\xff\xff\xffservers", header_type="client"
        ),
    }
