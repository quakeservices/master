import socket
import threading
import time
from socketserver import (BaseServer, DatagramRequestHandler,
                          ThreadingTCPServer, ThreadingUDPServer)

from helpers import LoggingMixin
from master import HealthCheckHandler, MasterHandler


class MasterServerUDP(ThreadingUDPServer):
    daemon_threads = True
    allow_reuse_address = True
    allow_reuse_port = True


class MasterServerTCP(ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True
    allow_reuse_port = True


class MasterServer(LoggingMixin):
    master_server: MasterServerUDP
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

    def _create_master_master(self, address: str, port: int):
        self.master_server = MasterServerUDP(
            (address, port),
            MasterHandler,
        )

    def _create_health_check_master(self, address: str, port: int):
        self.health_server = MasterServerTCP(
            (address, port),
            HealthCheckHandler,
        )

    @staticmethod
    def _create_thread(master, daemon: bool = True) -> threading.Thread:
        _thread = threading.Thread(target=master.serve_forever)
        _thread.daemon = daemon
        _thread.start()
        return _thread

    def start(self):
        with self.master_server, self.health_server:
            self.master_thread = self._create_thread(self.master_server)
            self.health_thread = self._create_thread(self.health_server)
            try:
                while self.alive():
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            finally:
                self.shutdown()

    def alive(self) -> bool:
        return self.master_thread.is_alive() and self.health_thread.is_alive()

    def shutdown(self):
        self.master_server.shutdown()
        self.health_server.shutdown()
