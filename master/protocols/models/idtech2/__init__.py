from pydantic import Field

from master.protocols.models import GameProtocol
from master.protocols.models.response import ProtocolResponse


class Idtech2Protocol(GameProtocol):
    engine: str = "idtech2"
    split: str = "\\"

    def process_data(
        self, received_header: bytes, data: list[bytes]
    ) -> ProtocolResponse:
        raise NotImplementedError
