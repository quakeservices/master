#
# pylint: disable=protected-access
# mypy: allow-untyped-defs
#
import pytest

from master.protocols import ProtocolResponse, Protocols
from master.protocols.models import GameProtocol, Quake2

find_protocol_fixtures = [
    pytest.param(b"\xff\xff\xff\xffping", Quake2(), "ping", id="ping"),
    pytest.param(b"\xff\xff\xff\xffgarbage", None, None, id="garbage"),
]

quake2_protocol_response_ping = ProtocolResponse(
    game="quake2",
    active=True,
    request_type="any",
    response_class="ping",
    response=b"\xff\xff\xff\xffack",
    players=[],
    details={},
)
quake2_protocol_response_heartbeat = ProtocolResponse(
    game="quake2",
    active=True,
    request_type="server",
    response_class="heartbeat",
    response=b"\xff\xff\xff\xffack",
    players=[
        {"score": "3", "ping": "5", "name": "player 1"},
        {"score": "4", "ping": "6", "name": "player 2"},
    ],
    details={"cheats": "0", "deathmatch": "1"},
)
quake2_protocol_response_shutdown = ProtocolResponse(
    game="quake2",
    active=False,
    request_type="server",
    response_class="shutdown",
    response=None,
    players=[],
    details={},
)
generate_response_fixtures = [
    pytest.param(
        Quake2(),
        b"\xff\xff\xff\xffping",
        "ping",
        quake2_protocol_response_ping,
        id="ping",
    ),
    pytest.param(
        Quake2(),
        b'\xff\xff\xff\xffheartbeat\n\\cheats\\0\\deathmatch\\1\n3 5 "player 1"\n4 6 "player 2"\n',
        "heartbeat",
        quake2_protocol_response_heartbeat,
        id="heartbeat",
    ),
    pytest.param(
        Quake2(),
        b"\xff\xff\xff\xffshutdown",
        "shutdown",
        quake2_protocol_response_shutdown,
        id="shutdown",
    ),
]
parse_request_fixtures = [
    pytest.param(
        b"\xff\xff\xff\xffping",
        quake2_protocol_response_ping,
        id="knownrequest",
    ),
    pytest.param(
        b"rAnDoMgArBaGeeee",
        None,
        id="unknownrequest",
    ),
]


@pytest.mark.protocols
@pytest.mark.unit_test
class TestProtocols:
    @pytest.fixture(scope="class")
    def protocols(self) -> Protocols:
        return Protocols()

    def test_protocols_load(self, protocols: Protocols) -> None:
        assert len(protocols.protocols) >= 1

    def test_protocols_check_proxy_protocol(self, protocols: Protocols) -> None:
        header = b"hello world"
        result = protocols._check_proxy_protocol(header)
        assert result == header

    @pytest.mark.parametrize(
        "test_input,expected_protocol,expected_response_class", find_protocol_fixtures
    )
    def test_protocols_find_protocol(
        self,
        protocols: Protocols,
        test_input: bytes,
        expected_protocol: GameProtocol,
        expected_response_class: str,
    ) -> None:
        protocol, response_class = protocols._find_protocol(test_input)
        assert protocol == expected_protocol
        assert response_class == expected_response_class

    @pytest.mark.parametrize(
        "test_protocol,test_request,test_response_class,expected_protocol_response",
        generate_response_fixtures,
    )
    def test_protocols_generate_response(
        self,
        protocols: Protocols,
        test_protocol: GameProtocol,
        test_request: bytes,
        test_response_class: str,
        expected_protocol_response: ProtocolResponse,
    ) -> None:
        protocol_response = protocols._generate_response(
            test_protocol, test_request, test_response_class
        )
        assert protocol_response == expected_protocol_response

    @pytest.mark.parametrize(
        "req,expected",
        parse_request_fixtures,
    )
    def test_parse_request(
        self, protocols: Protocols, req: bytes, expected: ProtocolResponse | None
    ) -> None:
        assert protocols.parse_request(req) == expected
