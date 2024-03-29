from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field  # pylint: disable=no-name-in-module


class BaseProtocol(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class BaseProtocolHeader(BaseModel):
    received: bytes = Field(description="Header received from client/server")
    response: Optional[bytes] = Field(
        description="Header to prefix response to client/server", default=None
    )
    header_type: Literal["any", "server", "client"] = Field(
        description=(
            "The type of header this correlates to; e.g."
            "some headers are only applicable to client requests"
        ),
        default="any",
    )


class BaseProtocolPlayerStatus(BaseModel):
    score: int = Field(description="Player score")
    player: str = Field(description="Player name")


Headers = dict[str, BaseProtocolHeader]
