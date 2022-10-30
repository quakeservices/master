#
# pylint: disable=protected-access
# mypy: allow-untyped-defs
#
from typing import Union

import pytest

from master.protocols.decoder import Decoder
from master.protocols.models import Quake2

find_response_class_fixtures = [
    pytest.param(b"\xff\xff\xff\xffping", "ping", id="ping"),
    pytest.param(b"\xff\xff\xff\xffgarbage", None, id="garbage"),
]

generate_metadata_fixtures = [
    pytest.param(
        "ping",
        {
            "request_type": "any",
            "game": "quake2",
            "response": b"\xff\xff\xff\xffack",
            "response_class": "ping",
            "active": True,
        },
        id="ping",
    ),
    pytest.param(
        "shutdown",
        {
            "request_type": "server",
            "game": "quake2",
            "response": None,
            "response_class": "shutdown",
            "active": False,
        },
        id="shutdown",
    ),
]

decode_details_fixtures = [
    pytest.param(
        b"\\cheats\\0\\deathmatch\\1\\dmflags\\16\\fraglimit\\0\\protocol\\34",
        {
            "cheats": "0",
            "deathmatch": "1",
            "dmflags": "16",
            "fraglimit": "0",
            "protocol": "34",
        },
        id="baseq2-details",
    )
]

decode_players_fixtures = [
    pytest.param(
        [b'5 4 "player 1"'],
        [{"score": "5", "ping": "4", "name": "player 1"}],
        id="one player",
    ),
    pytest.param(
        [b'5 4 "player 1"', b'6 1 "player 2"', b'3 2 "player 3"'],
        [
            {"score": "5", "ping": "4", "name": "player 1"},
            {"score": "6", "ping": "1", "name": "player 2"},
            {"score": "3", "ping": "2", "name": "player 3"},
        ],
        id="three players",
    ),
]


@pytest.mark.decoder
class TestDecoder:
    @pytest.fixture(scope="class")
    def decoder(self) -> Decoder:
        return Decoder(Quake2())

    def test_decode_bytes(self, decoder: Decoder):
        assert decoder._decode_bytes(b"hello world") == "hello world"

    @pytest.mark.parametrize("test_header,expected", find_response_class_fixtures)
    def test_find_response_class(
        self, decoder: Decoder, test_header: bytes, expected: Union[str, None]
    ):
        assert decoder._find_response_class(test_header) == expected

    @pytest.mark.parametrize("test_response_class,expected", generate_metadata_fixtures)
    def test_generate_metadata(
        self, decoder: Decoder, test_response_class: str, expected: dict
    ):
        decoder.response_class = test_response_class
        assert expected == decoder._generate_metadata()

    @pytest.mark.parametrize("test_details,expected", decode_details_fixtures)
    def test_decode_details(self, decoder: Decoder, test_details, expected: dict):
        assert expected == decoder._decode_details(test_details)

    @pytest.mark.parametrize("test_players,expected", decode_players_fixtures)
    def test_decode_players(self, decoder: Decoder, test_players, expected: dict):
        assert expected == decoder._decode_players(test_players)
