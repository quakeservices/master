from typing import Optional, Union

from protocols.models import BaseProtocolHeaders, Headers
from protocols.models.idtech2 import Idtech2Protocol
from protocols.models.response import ProtocolResponse
from protocols.utilities import dictify_players, dictify_status


class Quake2(Idtech2Protocol):
    game: str = "quake2"
    active: bool = True
    versions: list[str] = ["34"]
    headers: Headers = {
        "ping": BaseProtocolHeaders(
            received=b"\xff\xff\xff\xffping",
            response=b"\xff\xff\xff\xffack",
            type="any",
        ),
        "heartbeat": BaseProtocolHeaders(
            received=b"\xff\xff\xff\xffheartbeat",
            response=b"\xff\xff\xff\xffack",
            type="any",
        ),
        "shutdown": BaseProtocolHeaders(
            received=b"\xff\xff\xff\xffshutdown", type="server"
        ),
        "query": BaseProtocolHeaders(received=b"query", type="client"),
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
        details: dict[str, Union[str, int]] = {}
        players: list[Optional[dict[str, str]]] = []
        active: bool = True
        response: Optional[bytes] = None

        for name, header in self.headers.items():
            if received_header == header.received:
                response = header.response

                if name == "shutdown":
                    active = False

                break

        if len(data) >= 1:
            details = dictify_status(data[0], self.encoding, self.split)

        if len(data) >= 2:
            players = dictify_players(data[1:], self.encoding)

        return ProtocolResponse(
            game=self.game,
            active=active,
            details=details,
            players=players,
            response=response,
        )
