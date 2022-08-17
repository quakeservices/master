from master.protocols.models import BaseProtocolHeader, Headers
from master.protocols.models.idtech2 import Idtech2Protocol


class Quake2(Idtech2Protocol):
    game: str = "quake2"
    active: bool = True
    versions: list[str] = ["34"]
    headers: Headers = {
        "ping": BaseProtocolHeader(
            received=b"\xff\xff\xff\xffping",
            response=b"\xff\xff\xff\xffack",
            header_type="any",
        ),
        "heartbeat": BaseProtocolHeader(
            received=b"\xff\xff\xff\xffheartbeat",
            response=b"\xff\xff\xff\xffack",
            header_type="server",
        ),
        "shutdown": BaseProtocolHeader(
            received=b"\xff\xff\xff\xffshutdown", header_type="server"
        ),
        "query": BaseProtocolHeader(received=b"query", header_type="client"),
    }
    valid_status_keys: list[str] = [
        "cheats",
        "deathmatch",
        "dmflags",
        "fraglimit",
        "gamedate",
        "gamename",
        "hostname",
        "mapname",
        "maxclients",
        "maxspectators",
        "needpass",
        "protocol",
        "timelimit",
        "version",
    ]
