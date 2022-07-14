from typing import Optional, Union

from protocols.models import BaseProtocol
from pydantic import Field


class ProtocolResponse(BaseProtocol):
    game: str
    active: bool = Field(
        description=(
            "False in the event of a server sending a 'shutdown' request"
            "True all other times"
        )
    )
    header_type: str = "any"
    response: Optional[bytes] = None
    players: list[Optional[dict[str, str]]]
    details: dict[str, Union[str, int]]
