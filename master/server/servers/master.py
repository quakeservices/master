import logging
import threading
import time

from master.constants import DEFAULT_MASTER_PORT
from master.server.handlers import HealthCheckHandler, MasterHandler
from master.server.servers import HealthCheckServer, ThreadPoolServer
from master.storage import storage


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
        self.master_server = self._create_master_master(address, master_port)
        self.health_server = self._create_health_check_master(address, health_port)

    @staticmethod
    def _create_master_master(address: str, port: int) -> ThreadPoolServer:
        return ThreadPoolServer(
            (address, port),
            MasterHandler,
        )

    @staticmethod
    def _create_health_check_master(address: str, port: int) -> HealthCheckServer:
        return HealthCheckServer(
            (address, port),
            HealthCheckHandler,
        )

    @staticmethod
    def _create_thread(
        server: ThreadPoolServer | HealthCheckServer, name: str
    ) -> threading.Thread:
        _thread = threading.Thread(target=server.serve_forever, name=name, daemon=True)
        logging.debug("Starting thread %s", name)
        _thread.start()
        return _thread

    @staticmethod
    def initialise(storage_backend: str) -> None:
        """
        Anything that needs to be run before start is called.
        """
        storage_class = storage(backend=storage_backend)
        if storage_class:
            storage_class.initialise()
        else:
            raise Exception("Storage not found, unable to initialise")

    def start(self) -> None:
        with self.master_server, self.health_server:
            self.master_thread = self._create_thread(self.master_server, "master")
            self.health_thread = self._create_thread(self.health_server, "healthcheck")
            try:
                while self.alive():
                    time.sleep(3)
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
