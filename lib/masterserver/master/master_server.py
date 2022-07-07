import signal
import socket
import threading
import time
from socketserver import ThreadingTCPServer
from typing import Union

from helpers import LoggingMixin

from master import HealthCheckHandler, MasterHandler
from master.threadpool import ThreadPoolServer


class MasterServerTCP(ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True
    allow_reuse_port = True


class MasterServer(LoggingMixin):
    master_server: ThreadPoolServer
    master_thread: threading.Thread
    health_server: MasterServerTCP
    health_thread: threading.Thread
    default_address: str = socket.gethostbyname(socket.gethostname())
    default_master_port: int = 27900
    default_health_port: int = 8080

    def __init__(
        self,
        address: str = default_address,
        master_port: int = default_master_port,
        health_port: int = default_health_port,
    ):
        self._create_master_master(address, master_port)
        self._create_health_check_master(address, health_port)
        self._setup_signals()

    def _setup_signals(self) -> None:
        signal.signal(signal.SIGINT, self.shutdown())
        signal.signal(signal.SIGTERM, self.shutdown())

    def _create_master_master(self, address: str, port: int) -> None:
        self.master_server = ThreadPoolServer(
            (address, port),
            MasterHandler,
        )

    def _create_health_check_master(self, address: str, port: int) -> None:
        self.health_server = MasterServerTCP(
            (address, port),
            HealthCheckHandler,
        )

    @staticmethod
    def _create_thread(
        master: Union[ThreadPoolServer, MasterServerTCP], daemon: bool = True
    ) -> threading.Thread:
        _thread = threading.Thread(target=master.serve_forever)
        _thread.daemon = daemon
        _thread.start()
        return _thread

    def start(self) -> None:
        with self.master_server, self.health_server:
            self.master_thread = self._create_thread(self.master_server)
            self.health_thread = self._create_thread(self.health_server)
            try:
                while self.alive():
                    time.sleep(1)
            except KeyboardInterrupt:
                self.shutdown()
            finally:
                self.shutdown()

    def alive(self) -> bool:
        return self.master_thread.is_alive() and self.health_thread.is_alive()

    def shutdown(self) -> bool:
        self.master_server.terminate()
        self.master_server.shutdown()
        self.health_server.shutdown()
        return True
