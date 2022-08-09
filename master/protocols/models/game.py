from typing import Optional

from pydantic import Field

from master.protocols.models import BaseProtocol, Headers
from master.protocols.models.response import ProtocolResponse


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
    split: str = Field(description="String to split received data")
    newline: str = Field(description="String to lines", default="\n")

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
        raise NotImplementedError
