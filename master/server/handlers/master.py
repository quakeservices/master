import logging
import struct
from ipaddress import ip_address
from socketserver import DatagramRequestHandler
from typing import Optional

from master.protocols import ProtocolResponse, Protocols
from master.storage.backends import DynamoDbStorage
from master.storage.models.server import Server


class MasterHandler(DatagramRequestHandler):
    def handle(self) -> None:
        self.protocols = Protocols()
        self.storage = DynamoDbStorage()

        request: bytes = b""
        while True:
            fragment: bytes = self.rfile.readline()
            logging.debug(f"Recieved fragment {fragment!r} from {self.client_address}")
            if fragment != b"":
                request = request + fragment
            else:
                break

        logging.info(f"Recieved {request!r} from {self.client_address}")

        protocol_response: Optional[ProtocolResponse] = self.protocols.parse_request(
            request
        )
        if protocol_response:
            response: Optional[bytes] = None
            if protocol_response.request_type == "client":
                response = self._handle_client_request(protocol_response)
            elif protocol_response.request_type == "server":
                response = self._handle_server_request(protocol_response)
            elif protocol_response.request_type == "any":
                response = self._handle_generic_request(protocol_response)

            if response:
                self._send_response(response)

    def _send_response(self, response: bytes) -> None:
        logging.debug(f"Sending {response!r} to {self.client_address}")
        self.wfile.write(response)

    def _handle_client_request(self, request: ProtocolResponse) -> bytes:
        logging.debug("Header belongs to client")

        server_list: list[Server] = self.storage.get_servers(request.game)
        processed_server_list: list[bytes] = [
            self._pack_address(server.address) for server in server_list
        ]

        return self._create_response(processed_server_list, request.response)

    def _handle_server_request(self, request: ProtocolResponse) -> Optional[bytes]:
        logging.debug("Header belongs to server")
        address = ":".join([self.client_address[0], str(self.client_address[1])])
        server = Server(
            address=address,
            game=request.game,
            active=request.active,
            details=request.details,
            players=request.players,
        )

        self.storage.update_server(server)

        return request.response

    def _handle_generic_request(self, request: ProtocolResponse) -> Optional[bytes]:
        if request.response:
            return request.response

        return None

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
