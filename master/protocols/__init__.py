import logging
from typing import Optional

from master.protocols.decoder import Decoder
from master.protocols.models import GameProtocol, Quake2
from master.protocols.models.response import ProtocolResponse


class Protocols:
    protocols: list[GameProtocol] = [Quake2()]

    def _check_proxy_protocol(self, request: bytes) -> bytes:
        """
        Not implemented
        """
        return request

    def _find_protocol(self, request_header: bytes) -> Optional[GameProtocol]:
        for protocol in self.protocols:
            if protocol.match_header(request_header):
                return protocol

        return None

    def parse_request(self, request: bytes) -> Optional[ProtocolResponse]:
        response: Optional[ProtocolResponse] = None

        parsed_request: bytes = self._check_proxy_protocol(request)
        request_header, *_ = parsed_request.splitlines()

        protocol = self._find_protocol(request_header)
        if protocol:
            _response = protocol.process_request(request_header)
            decoder = Decoder(protocol)
            _response.update(decoder.decode(parsed_request))
            response = ProtocolResponse.parse_obj(_response)

        return response
