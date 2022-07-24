from typing import Optional, Union

from pydantic import Field

from master.protocols.models import BaseProtocol


class ProtocolResponse(BaseProtocol):
    game: str
    active: bool = Field(
        default=True,
        description=(
            "False in the event of a server sending a 'shutdown' request"
            "True all other times"
        ),
    )
    request_type: str
    response_class: str
    response: Optional[bytes] = Field(default=None)
    players: list[Optional[dict[str, str]]] = Field(defaultfactory=list)
    details: dict[str, Union[str, int]] = Field(defaultfactory=dict)
