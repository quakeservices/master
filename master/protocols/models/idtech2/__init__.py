from pydantic import Field

from master.protocols.models import GameProtocol


class Idtech2Protocol(GameProtocol):
    engine: str = "idtech2"
    split: str = Field(description="String to split received data", default="\\")
