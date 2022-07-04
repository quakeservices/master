from protocols.models import GameProtocol
from pydantic import Field


class Idtech2Protocol(GameProtocol):
    engine: str = "idtech2"
    split: str = Field(description="String to split received data", default="\\")
