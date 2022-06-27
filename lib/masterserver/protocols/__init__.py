from typing import Optional

from protocols.models import GameProtocol, ProtocolResponse, Quake2
from protocols.proxy import ProxyProtocol


class Protocols:
    protocols: list[GameProtocol] = [Quake2()]

    @staticmethod
    def _check_proxy_protocol(request: bytes) -> bytes:
        parsed_request: bytes = b""

        if len(request) >= 16:
            parsed_request = ProxyProtocol.parse_request(request)
        else:
            parsed_request = request

        return parsed_request

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
            response = protocol.process_data(status)

        return response
