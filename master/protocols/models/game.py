from typing import Optional, Union

from pydantic import Field

from master.protocols.models import BaseProtocol, Headers


class GameProtocol(BaseProtocol):
    engine: str = Field(description="Short name of the engine; e.g.: idtech2")
    game: str = Field(description="Short name of the engine; e.g.: quake2")
    encoding: str = Field(
        description="Encoding to use when decoding data received", default="latin1"
    )
    active: bool = Field(
        description="Whether the protocol is active and will be checked against received headers",
        default=False,
    )
    versions: list[str] = Field(
        description="Versions of the game this protocol applies to"
    )
    headers: Headers = Field(description="Header definitions")
    valid_status_keys: Optional[list[str]] = Field(
        description="List of expected keys when parsing a server status",
        default_factory=list,
    )
    split_details: str = Field(description="String to split received server details")
    split_players: str = Field(
        description="String to split received player information"
    )
    newline: str = Field(description="String to lines", default="\n")

    def match_header(self, received_header: bytes) -> bool:
        if not self.active:
            return False

        for _, header_data in self.headers.items():
            if header_data.received == received_header:
                return True

        return False

    def process_request(
        self, received_header: bytes
    ) -> dict[str, Union[str, bool, bytes]]:

        for header_name, header in self.headers.items():
            if received_header == header.received:
                active: bool = True
                if header_name == "shutdown":
                    active = False

                return {
                    "request_type": header.header_type,
                    "game": self.game,
                    "response": header.response,
                    "response_class": header_name,
                    "active": active,
                }

        return {}
