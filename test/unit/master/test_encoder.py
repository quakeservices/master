#
# pylint: disable=protected-access
# mypy: allow-untyped-defs
#
from typing import Union

import pytest

from master.protocols.encoder import Encoder
from master.protocols.models import Quake2

encode_details_fixtures = [
    pytest.param(
        {"cheats": "1", "deathmatch": "1"},
        b"\\cheats\\1\\deathmatch\\1",
        id="details_fixture_1",
    ),
    pytest.param(
        {"cheats": "0", "deathmatch": "0"},
        b"\\cheats\\0\\deathmatch\\0",
        id="details_fixture_2",
    ),
    pytest.param(
        None,
        b"",
        id="details_fixture_empty",
    ),
]
encode_players_fixtures = [
    pytest.param(
        [{"score": "1", "ping": "1", "name": "player 1"}],
        b'1 1 "player 1"',
        id="players_fixture_1",
    ),
    pytest.param(
        [
            {"score": "1", "ping": "1", "name": "player 1"},
            {"score": "2", "ping": "2", "name": "player 2"},
        ],
        b'1 1 "player 1"\n2 2 "player 2"',
        id="players_fixture_2",
    ),
    pytest.param(
        None,
        b"",
        id="players_fixture_empty",
    ),
]


@pytest.mark.encoder
class TestEncoder:
    @pytest.fixture(scope="class")
    def encoder(self) -> Encoder:
        return Encoder(Quake2())

    @pytest.mark.parametrize("test_details,expected", encode_details_fixtures)
    def test_encode_details(
        self, encoder: Encoder, test_details: Union[dict, None], expected: bytes
    ):
        assert encoder._encode_details(test_details) == expected

    @pytest.mark.parametrize("test_players,expected", encode_players_fixtures)
    def test_encode_players(
        self, encoder: Encoder, test_players: Union[list[dict], None], expected: bytes
    ):
        assert encoder._encode_players(test_players) == expected
