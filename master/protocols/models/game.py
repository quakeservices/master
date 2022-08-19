from typing import Optional

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

    def match_header(self, received_header: bytes) -> tuple[bool, Optional[str]]:
        if not self.active:
            return False, None

        for response_class, header in self.headers.items():
            if received_header.startswith(header.received):
                return True, response_class

        return False, None
