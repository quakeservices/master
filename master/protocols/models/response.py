from typing import Literal

from pydantic import Field

from master.protocols.models import BaseProtocol


class ProtocolResponse(BaseProtocol):
    game: str = Field(description="Name of the game")
    active: bool = Field(
        default=True,
        description=(
            "False in the event of a server sending a 'shutdown' request"
            "True all other times"
        ),
    )
    request_type: Literal["client", "server", "any"] = Field(
        description="Type of request"
    )
    response_class: Literal["ping", "heartbeat", "shutdown", "query"] = Field(
        description="Response class"
    )
    response: bytes | None = Field(default=None, description="Response header")
    players: list[dict[str, str]] = Field(
        default_factory=list,
        description=("List of server players if response belongs to a server"),
    )
    details: dict[str, str | int] = Field(
        default_factory=dict,
        description=("Server details if response belongs to a server"),
    )
