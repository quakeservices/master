from typing import Literal, Optional, Union

from protocols.models import BaseProtocol


class ProtocolResponse(BaseProtocol):
    header_type: str = "any"
    response: Optional[bytes] = None
    players: list[Optional[dict[str, str]]]
    status: dict[str, Union[str, int]]
