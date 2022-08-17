import re
from typing import Optional, Union

from master.protocols.models.game import GameProtocol


class Decoder:
    protocol: GameProtocol
    newline: str
    player_regex = re.compile(
        r'(?P<score>-?\d+) (?P<ping>-?\d+) "(?P<name>.+)"', flags=re.ASCII
    )

    def __init__(self, protocol: GameProtocol) -> None:
        self.protocol = protocol

    def decode(self, data: bytes) -> dict:
        result: dict[
            str,
            Union[str, dict[str, str], list[Optional[dict[str, str]]]],
        ] = {}

        newline: bytes = self.protocol.newline.encode(self.protocol.encoding)
        lines: list[bytes] = [line for line in data.split(newline) if line]

        if len(lines) >= 1:
            # header only
            result["header"] = self._decode_header(lines[1])

        if len(lines) >= 2:
            # header and details
            result["details"] = self._decode_details(lines[2])

        if len(lines) >= 3:
            # header, details, and players
            result["players"] = self._decode_players(lines[3:])

        return result

    def _decode_header(self, header: bytes) -> str:
        return self._decode_bytes(header)

    def _decode_details(self, details: bytes) -> dict[str, str]:
        """
        Convert a byte string into a dict
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
        Convert a list of bytes into a list of dicts if they match regex
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
