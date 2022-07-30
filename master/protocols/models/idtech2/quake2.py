from typing import Optional, Union

from master.protocols.models import BaseProtocolHeader, Headers
from master.protocols.models.idtech2 import Idtech2Protocol
from master.protocols.models.response import ProtocolResponse
from master.protocols.utilities import dictify_players, dictify_status


class Quake2(Idtech2Protocol):
    game: str = "quake2"
    active: bool = True
    versions: list[str] = ["34"]
    headers: Headers = {
        "ping": BaseProtocolHeader(
            received=b"\xff\xff\xff\xffping",
            response=b"\xff\xff\xff\xffack",
            type="any",
        ),
        "heartbeat": BaseProtocolHeader(
            received=b"\xff\xff\xff\xffheartbeat",
            response=b"\xff\xff\xff\xffack",
            type="server",
        ),
        "shutdown": BaseProtocolHeader(
            received=b"\xff\xff\xff\xffshutdown", type="server"
        ),
        "query": BaseProtocolHeader(received=b"query", type="client"),
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

    def match_header(self, received_header: bytes) -> bool:
        if not self.active:
            return False

        for _, header_data in self.headers.items():
            if header_data.received == received_header:
                return True

        return False

    def process_data(
        self, received_header: bytes, data: list[bytes]
    ) -> ProtocolResponse:
        response_map: dict = {"details": {}, "players": []}

        for header_name, header in self.headers.items():
            if received_header == header.received:
                response_map["request_type"] = header.type
                response_map["game"] = self.game
                response_map["response"] = header.response
                response_map["response_class"] = header_name

                if header_name == "shutdown":
                    response_map["active"] = False

                break

        if len(data) >= 1:
            response_map["details"] = dictify_status(data[0], self.encoding, self.split)

        if len(data) >= 2:
            response_map["players"] = dictify_players(data[1:], self.encoding)

        return ProtocolResponse.parse_obj(response_map)
