from collections.abc import Mapping
from typing import Optional

from protocols.models import (BaseProtocol, BaseProtocolHeaders,
                              ProtocolResponse)
from pydantic import Field


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
    headers: Mapping[str, BaseProtocolHeaders] = Field(description="Header definitions")
    valid_status_keys: Optional[list[str]] = Field(
        description="List of expected keys when parsing a server status",
        default_factory=list,
    )

    def match_header(self, received_header: bytes) -> bool:
        raise NotImplementedError

    def process_data(self, data: list[bytes]) -> ProtocolResponse:
        raise NotImplementedError
