import pytest
from lib.masterserver.protocols import ProtocolResponse, Protocols


class TestProtocols:
    @pytest.fixture(scope="class")
    def protocols(self):
        return Protocols()

    def test_protocols_load(self, protocols):
        assert len(protocols.protocols) >= 1

    def test_find_protocol(self, protocols):
        header: bytes = b"ping"
        result = protocols._find_protocol(header)
        assert isinstance(result, ProtocolResponse)
