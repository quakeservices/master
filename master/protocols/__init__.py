import logging
from typing import Optional

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
        request_header, *status = parsed_request.splitlines()

        protocol = self._find_protocol(request_header)
        if protocol:
            response = protocol.process_data(request_header, status)

        return response
