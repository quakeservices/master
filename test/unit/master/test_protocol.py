import pytest

from master.protocols import ProtocolResponse, Protocols
from master.protocols.models import GameProtocol


class TestProtocols:
    @pytest.fixture(scope="class")
    def protocols(self):
        return Protocols()

    @pytest.fixture(scope="class")
    def header_ping(self) -> bytes:
        return b"\xff\xff\xff\xffping"

    def test_protocols_load(self, protocols):
        assert len(protocols.protocols) >= 1

    def test_protocols__check_proxy_protocol(self, protocols, header_ping):
        result = protocols._check_proxy_protocol(header_ping)
        assert result == header_ping

    def test_protocols__find_protocol(self, protocols, header_ping):
        result = protocols._find_protocol(header_ping)
        assert isinstance(result, GameProtocol)

    def test_protocols_parse_request_valid_header(self, protocols, header_ping):
        result = protocols.parse_request(header_ping)
        assert isinstance(result, ProtocolResponse)

    def test_protocols_parse_request_invalid_header(self, protocols):
        result = protocols.parse_request(b"Hot Garbage")
        assert result is None
