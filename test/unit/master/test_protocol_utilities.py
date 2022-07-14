from typing import Union

import pytest

from lib.masterserver.protocols.utilities import dictify_players, dictify_status


class TestDictifyPlayers:
    @pytest.fixture(scope="class")
    def players(self) -> list[bytes]:
        """
        score, ping, name
        """
        return [
            b'4 123 "normal-player"',
            b'-5 14 "shit_player"',
        ]

    @pytest.fixture(scope="class")
    def encoding(self) -> str:
        return "latin1"

    @pytest.fixture(scope="class")
    def expected_players(self) -> list[dict[str, str]]:
        return [
            {"score": "4", "ping": "123", "name": "normal-player"},
            {"score": "-5", "ping": "14", "name": "shit_player"},
        ]

    def test_dictify_players(self, players, encoding, expected_players):
        result = dictify_players(players, encoding)
        assert result == expected_players


class TestDictifyStatus:
    @pytest.fixture(scope="class")
    def status(self) -> bytes:
        return b"\\cheats\\0\\deathmatch\\1\\"

    @pytest.fixture(scope="class")
    def encoding(self) -> str:
        return "latin1"

    @pytest.fixture(scope="class")
    def split(self) -> str:
        return "\\"

    @pytest.fixture(scope="class")
    def expected_status(self) -> dict[str, Union[int, str]]:
        return {"cheats": 0, "deathmatch": 1}

    def test_dictify_status(self, status, encoding, split, expected_status):
        result = dictify_status(status, encoding, split)
        assert result == expected_status
