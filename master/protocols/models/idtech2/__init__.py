from master.protocols.models import GameProtocol


class Idtech2Protocol(GameProtocol):
    engine: str = "idtech2"
    split_details: str = "\\"
    split_players: str = " "
