import logging
from typing import Optional

from master.protocols.decoder import Decoder
from master.protocols.models import ALL_ACTIVE_PROTOCOLS, GameProtocol
from master.protocols.models.response import ProtocolResponse


class Protocols:
    protocols: list[GameProtocol] = ALL_ACTIVE_PROTOCOLS

    def _check_proxy_protocol(self, request: bytes) -> bytes:
        """
        Check if request contains ProxyProtocol headers and strip them out if so.
        Not currently required so not implemented.
        """
        return request

    def _find_protocol(
        self, request_header: bytes
    ) -> tuple[Optional[GameProtocol], Optional[str]]:
        """
        Find the protocol that matches a given header
        """
        for protocol in self.protocols:
            match, response_class = protocol.match_header(request_header)
            if match:
                return protocol, response_class

        return None, None

    def _generate_response(
        self, protocol: GameProtocol, request: bytes, response_class: str
    ) -> ProtocolResponse:
        """
        Decode the request into a ProtocolResponse
        """
        decoder = Decoder(protocol, response_class)
        return decoder.generate_protocol_response(request)

    def parse_request(self, request: bytes) -> Optional[ProtocolResponse]:
        parsed_request: bytes = self._check_proxy_protocol(request)
        first_line, *_ = parsed_request.splitlines()
        # Shouldn't need more than the first 16 bytes of the header
        request_header: bytes = first_line[:16]

        protocol, response_class = self._find_protocol(request_header)
        if protocol:
            return self._generate_response(protocol, request, response_class)

        return None
