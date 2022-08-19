from pydantic import Field

from master.protocols.models import GameProtocol
from master.protocols.models.response import ProtocolResponse


class Idtech3Protocol(GameProtocol):
    engine: str = "idtech3"
    split_details: str = "\\"
    split_players: str = " "
