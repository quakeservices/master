import re
from typing import Optional, Union

from master.protocols.models.game import GameProtocol
from master.protocols.models.response import ProtocolResponse

ResultTypeDict = dict[
    str,
    Union[str, bytes, bool, dict[str, str], list[Optional[dict[str, str]]]],
]

# TODO: Move player_regex into GameProtocol?


class Decoder:
    protocol: GameProtocol
    response_class: Optional[str]
    newline: str
    player_regex: re.Pattern = re.compile(
        r'(?P<score>-?\d+) (?P<ping>-?\d+) "(?P<name>.+)"', flags=re.ASCII
    )

    def __init__(
        self, protocol: GameProtocol, response_class: Optional[str] = None
    ) -> None:
        self.protocol = protocol
        self.response_class = response_class

    def decode(self, data: bytes) -> dict:
        result: ResultTypeDict = {"details": {}, "players": []}
        newline: bytes = self.protocol.newline.encode(self.protocol.encoding)
        lines: list[bytes] = [line for line in data.split(newline) if line]

        if len(lines) >= 1:
            # header
            if not self.response_class:
                self._find_response_class(lines[0])

            result = self._generate_metadata()

        if len(lines) >= 2:
            # header and details
            result["details"] = self._decode_details(lines[1])

        if len(lines) >= 3:
            # header, details, and players
            result["players"] = self._decode_players(lines[2:])

        return result

    def generate_protocol_response(self, data: bytes) -> ProtocolResponse:
        response = self.decode(data)
        return ProtocolResponse.parse_obj(response)

    def _generate_metadata(self) -> ResultTypeDict:
        """
        Generate information to populate ProtocolResponse
        """
        active: bool = True
        if self.response_class == "shutdown":
            active = False

        return {
            "request_type": self.protocol.headers[self.response_class].header_type,
            "game": self.protocol.game,
            "response": self.protocol.headers[self.response_class].response,
            "response_class": self.response_class,
            "active": active,
        }

    def _find_response_class(self, received_header: bytes) -> Optional[str]:
        for response_class, header in self.protocol.headers.items():
            if received_header.startswith(header.received):
                return response_class

        return None

    def _decode_header(self, header: bytes) -> str:
        return self._decode_bytes(header)

    def _decode_details(self, details: bytes) -> dict[str, str]:
        """
        Convert a byte string containing server information into a dict

        For example:
            Input:
                b"\\cheats\\0\\deathmatch\\1\\dmflags\\16\\fraglimit\\0\\protocol\\34"
            Output:
                {
                    "cheats": "0",
                    "deathmatch": "1",
                    "dmflags": "16",
                    "fraglimit": "0",
                    "protocol": "34",
                }
        """
        # Split details, remove any blank strings, and truncate values
        list_details: list[str] = [
            detail[:128]
            for detail in self._decode_bytes(details).split(self.protocol.split_details)
            if detail
        ]

        # If the length of details isn't even, truncate the last value
        if len(list_details) % 2 != 0:
            list_details = list_details[:-1]

        # Coalesce list into key:value pairs
        # from: ["a", 1, "b", 2]
        # to:   {"a": 1, "b": 2}
        return dict(zip(list_details[0::2], list_details[1::2]))

    def _decode_players(self, players: list[bytes]) -> list[Optional[dict[str, str]]]:
        """
        Convert a list of bytes containing player information into a list of dicts if they match player_regex

        For example:
            Input:
                [b'1 3 "player 1", b'5 5 "player 2"']
            Output:
                [
                    {"score": "1", "ping": "3", "name": "player 1"},
                    {"score": "5", "ping": "5", "name": "player 2"},
                ]
        """
        result: list[Optional[dict[str, str]]] = []
        for player in players:
            player_match: re.Match[str] = re.match(
                self.player_regex, self._decode_bytes(player)
            )
            if player_match:
                result.append(player_match.groupdict())

        return result

    def _decode_bytes(self, data: bytes) -> str:
        return data.decode(self.protocol.encoding)
