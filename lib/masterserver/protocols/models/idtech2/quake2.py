from typing import Optional, Union

from protocols.models import BaseProtocolHeaders, GameProtocol, ProtocolResponse
from protocols.models.idtech2 import Idtech2Protocol
from protocols.utilities import dictify_players, dictify_status
from pydantic import Field


class Quake2(GameProtocol, Idtech2Protocol):
    game = "quake2"
    active = True
    versions = ["34"]
    headers = {
        "ping": BaseProtocolHeaders(
            receive=b"\xff\xff\xff\xffping",
            response=b"\xff\xff\xff\xffack",
            type="any",
        ),
        "heartbeat": BaseProtocolHeaders(
            receive=b"\xff\xff\xff\xffheartbeat",
            response=b"\xff\xff\xff\xffack",
            type="any",
        ),
        "shutdown": BaseProtocolHeaders(
            receive=b"\xff\xff\xff\xffshutdown", type="server"
        ),
        "query": BaseProtocolHeaders(receive=b"query", type="client"),
    }
    valid_status_keys = [
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
            if header_data.receive == received_header:
                return True

        return False

    def process_data(self, data: list[bytes]) -> ProtocolResponse:
        status: dict[str, Union[str, int]] = {}
        players: list[Optional[dict[str, str]]] = []

        if len(data) >= 1:
            status = dictify_status(data[0], self.encoding, self.split)

        if len(data) >= 2:
            players = dictify_players(data[1:], self.encoding)

        return ProtocolResponse(
            status=status,
            players=players,
        )
