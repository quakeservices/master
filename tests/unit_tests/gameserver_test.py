import pytest

from gameserver import GameServer


@pytest.fixture
def server_status():
    address = ("127.0.0.1", 27910)
    result = {
        "active": True,
        "encoding": "latin1",
        "split_on": "\\",
        "status": [
            b"\\cheats\\0\\deathmatch\\1\\dmflags\\16\\fraglimit\\0",
            b"10 15 Player One\n",
        ],
    }
    return GameServer(address, result)


def test_properties(server_status):
    assert server_status.active == True
    assert server_status.encoding == "latin1"
    assert server_status.ip == "127.0.0.1"
    assert server_status.port == 27910
    assert server_status.address == "127.0.0.1:27910"


def test_status(server_status):
    assert server_status.status.get("fraglimit", -1) == 0
    assert server_status.status.get("dmflags", -1) == 16
    assert server_status.status.get("deathmatch", -1) == 1
    assert server_status.status.get("cheats", -1) == 0
