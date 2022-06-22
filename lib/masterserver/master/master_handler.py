import struct
from dataclasses import asdict
from ipaddress import ip_address
from socketserver import DatagramRequestHandler
from typing import Optional

from gameserver import GameServer
from helpers import LoggingMixin
from protocols import GameProtocolResponse, GameProtocols
from storage import PynamoDbStorage


class MasterHandler(DatagramRequestHandler, LoggingMixin):
    def handle(self):
        self.log("Initialising master server.")
        self.storage = PynamoDbStorage()
        # TODO: Share this between threads?
        self.protocols = GameProtocols()

        request: bytes = b""
        while True:
            fragment: bytes = self.rfile.readline()
            self.log(f"Recieved fragment {fragment!r} from {self.client_address}")
            if fragment != b"":
                request = request + fragment
            else:
                break

        self.log(f"Recieved {request!r} from {self.client_address}")
        response: Optional[bytes] = None

        protocol_response: GameProtocolResponse = self.protocols.parse_request(request)
        self.log(f"{asdict(protocol_response)}")
        if protocol_response.header_match:
            if protocol_response.header_type == "client":
                response = self._handle_client_request(protocol_response)
            elif protocol_response.header_type in ("server", "any"):
                response = self._handle_server_request(protocol_response)

            if response:
                self._send_response(response)

    def _send_response(self, response: bytes):
        self.log(f"Sending {response!r} to {self.client_address}")
        self.wfile.write(response)

    def _handle_client_request(self, request: GameProtocolResponse) -> bytes:
        self.log("Header belongs to client")

        response_header: Optional[bytes] = request.response
        server_list: list[str] = self.storage.list_server_addresses(request.game)
        server_list = [""]
        processed_server_list: list[bytes] = [
            self._pack_address(server) for server in server_list
        ]
        return self._create_response(processed_server_list, response_header)

    def _handle_server_request(self, request: GameProtocolResponse) -> Optional[bytes]:
        self.log("Header belongs to server")
        server = GameServer(self.client_address, request)
        if server.active:
            self.storage.save_server(server)
        else:
            self.storage.server_shutdown(server)

        return request.response

    @staticmethod
    def _create_response(
        response: list[bytes],
        header: Optional[bytes] = None,
        seperator: bytes = b"",
    ) -> bytes:

        if header:
            response.insert(0, header)

        return seperator.join(response)

    @staticmethod
    def _pack_address(address: str, port_format: str = ">H") -> bytes:
        """
        >H = unsigned short
        Takes string formatted address;
        eg, '192.168.0.1:27910'
        Converts to 6 byte binary string.
        """
        server_ip: str
        server_port: str

        server_ip, server_port = address.split(":")

        server_ip_bytes: bytes = ip_address(server_ip).packed
        server_port_bytes: bytes = struct.pack(port_format, int(server_port))

        return server_ip_bytes + server_port_bytes
