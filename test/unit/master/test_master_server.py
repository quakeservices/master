from threading import Thread

import pytest

from master.server.handlers import HealthCheckHandler
from master.server.servers import HealthCheckServer, ThreadPoolServer
from master.server.servers.master import MasterServer


@pytest.mark.master_server
@pytest.mark.unit
class TestMasterServer:
    def test_create_master_server(self) -> None:
        server = MasterServer._create_master_master("127.0.0.1", 29710)
        assert isinstance(server, ThreadPoolServer)

    def test_create_health_check_master(self) -> None:
        server = MasterServer._create_health_check_master("127.0.0.1", 29710)
        assert isinstance(server, HealthCheckServer)

    def test_create_thread(self) -> None:
        server = HealthCheckServer(("127.0.0.1", 8080), HealthCheckHandler)
        thread = MasterServer._create_thread(server, "testing")
        assert isinstance(thread, Thread)
        assert thread.name == "testing"
        assert thread.daemon
        assert thread.is_alive()
