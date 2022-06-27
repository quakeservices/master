from protocols.models import BaseProtocol
from pydantic import Field


class Idtech2Protocol(BaseProtocol):
    engine = "idtech2"
    split: str = Field(description="String to split received data", default="\\")
