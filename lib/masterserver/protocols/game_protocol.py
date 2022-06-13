import logging
from dataclasses import dataclass, field
from typing import Literal, Optional, Union

HeaderClasses = Literal["any", "server", "client"]
HeaderCommand = Literal["ping", "query", "heartbeat", "shutdown"]
HeaderMessage = Literal["recv", "resp", "type"]

Headers = dict[HeaderCommand, dict[HeaderMessage, str]]
EncodedHeaders = dict[HeaderCommand, dict[HeaderMessage, bytes]]


@dataclass
class GameProtocolResponse:
    # TODO: Merge with ProtocolResponse
    game: str
    encoding: str
    header_type: Optional[str] = None
    response: Optional[bytes] = None
    active: bool = False
    header_match: bool = False


@dataclass
class GameProtocol:
    game: str
    engine: str
    version: int
    headers: Headers
    status_keys: list[dict[Literal["key", "integer"], Union[str, bool]]]
    misc: dict
    active: bool = False
    encoding: str = "latin1"
    _encoded_headers: EncodedHeaders = field(default_factory=dict)

    def __post_init__(self):
        logging.debug(
            f"{self.__class__.__name__ } - Initialising protocols for {self.game}"
        )
        self._encode_headers()

    def __repr__(self) -> str:
        return self.game

    def match_receive_header(self, header_to_check: bytes) -> GameProtocolResponse:
        response: GameProtocolResponse = GameProtocolResponse(
            game=self.game, encoding=self.encoding
        )
        for command, message in self._encoded_headers.items():
            if message.get("recv", b"").startswith(header_to_check):
                response.response = message.get("resp", None)
                response.header_match = True
                response.header_type = self.headers[command]["type"]

                if command != "shutdown":
                    response.active = True

                return response

        return response

    def _encode_headers(self):
        for command, messages in self.headers.items():
            self._encoded_headers[command] = {}
            for message_type, message in messages.items():
                self._encoded_headers[command][message_type] = self._encode(message)

    def _encode(self, data: str) -> bytes:
        return bytes(data, self.encoding, errors="backslashreplace")
