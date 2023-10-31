from master.protocols.models import GameProtocol
from master.protocols.models.response import ProtocolResponse


class Idtech1Protocol(GameProtocol):
    engine: str = "idtech1"
    split_details: str = "\\"
    split_players: str = " "
