from typing import Optional

from master.protocols.models import BaseProtocolHeader
from master.protocols.models.game import GameProtocol


class Encoder:
    protocol: GameProtocol

    def __init__(self, protocol: GameProtocol) -> None:
        self.protocol = protocol

    def encode(
        self,
        request: str,
        details: Optional[dict] = None,
        players: Optional[list[dict]] = None,
    ) -> bytes:
        header: BaseProtocolHeader = self.protocol.headers.get(request)
        newline: bytes = self.protocol.newline.encode(self.protocol.encoding)
        response: list[bytes] = [
            header.received,
            self._encode_details(details),
            self._encode_players(players),
        ]
        return newline.join([item for item in response if item])

    def _encode_details(self, details: Optional[dict] = None) -> bytes:
        if details:
            split: str = self.protocol.split_details
            _details: list[str] = [
                split.join([key, value]) for key, value in details.items()
            ]
            _details.insert(0, split)
            result: str = split.join(_details)
            return result.encode(self.protocol.encoding)

        return b""

    def _encode_players(self, players: Optional[list[dict[str, str]]]) -> bytes:
        if players:
            result: str = self.protocol.newline.join(
                [
                    self.protocol.split_players.join(
                        [player["score"], player["ping"], f'"{player["name"]}"']
                    )
                    for player in players
                ]
            )
            return result.encode(self.protocol.encoding)

        return b""
