from master.protocols.models.base import (
    BaseProtocol,
    BaseProtocolHeader,
    BaseProtocolPlayerStatus,
    Headers,
)
from master.protocols.models.game import GameProtocol
from master.protocols.models.idtech1.quakeworld import QuakeWorld
from master.protocols.models.idtech2.quake2 import Quake2
from master.protocols.models.idtech3.quake3 import Quake3

__all__ = ["Quake2"]

ALL_PROTOCOLS: list[GameProtocol] = [QuakeWorld(), Quake2(), Quake3()]
ALL_ACTIVE_PROTOCOLS: list[GameProtocol] = [
    protocol for protocol in ALL_PROTOCOLS if protocol.active
]
