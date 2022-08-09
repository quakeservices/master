import signal
import threading
import time
from typing import Union

from master.constants import DEFAULT_MASTER_PORT
from master.server.handlers import HealthCheckHandler, MasterHandler
from master.server.servers import HealthCheckServer, ThreadPoolServer
from master.storage.backends.dynamodb import DynamoDbStorage


class MasterServer:
    master_server: ThreadPoolServer
    master_thread: threading.Thread
    health_server: HealthCheckServer
    health_thread: threading.Thread
    default_address: str = "0.0.0.0"
    default_master_port: int = DEFAULT_MASTER_PORT
    default_health_port: int = 8080

    def __init__(
        self,
        address: str = default_address,
        master_port: int = default_master_port,
        health_port: int = default_health_port,
    ):
        self._create_master_master(address, master_port)
        self._create_health_check_master(address, health_port)
        # self._setup_signals()

    def _setup_signals(self) -> None:
        signal.signal(signal.SIGINT, self.shutdown())
        signal.signal(signal.SIGTERM, self.shutdown())

    def _create_master_master(self, address: str, port: int) -> None:
        self.master_server = ThreadPoolServer(
            (address, port),
            MasterHandler,
        )

    def _create_health_check_master(self, address: str, port: int) -> None:
        self.health_server = HealthCheckServer(
            (address, port),
            HealthCheckHandler,
        )

    @staticmethod
    def _create_thread(
        server: Union[ThreadPoolServer, HealthCheckServer], daemon: bool = True
    ) -> threading.Thread:
        _thread = threading.Thread(target=server.serve_forever)
        _thread.daemon = daemon
        _thread.start()
        return _thread

    def initialise(self) -> None:
        storage = DynamoDbStorage()
        storage.initialise()

    def start(self) -> None:
        with self.master_server, self.health_server:
            self.master_thread = self._create_thread(self.master_server)
            self.health_thread = self._create_thread(self.health_server)
            try:
                while self.alive():
                    time.sleep(5)
            except KeyboardInterrupt:
                pass
            finally:
                self.shutdown()

    def alive(self) -> bool:
        return self.master_thread.is_alive() and self.health_thread.is_alive()

    def shutdown(self) -> bool:
        self.master_server.shutdown()
        self.health_server.shutdown()
        while self.alive():
            continue

        return True
