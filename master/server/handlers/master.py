import logging
import struct
from ipaddress import ip_address
from socketserver import DatagramRequestHandler

from master.protocols import ProtocolResponse, Protocols
from master.storage import storage
from master.storage.models.server import Server


class MasterHandler(DatagramRequestHandler):
    def handle(self) -> None:
        storage_class = storage(backend="dynamodb")
        if storage_class:
            self.storage = storage_class()  # pylint: disable=not-callable

        request: bytes = self.__get_request()
        if request:
            self.__handle_request(request)

    def __get_request(self) -> bytes:
        request: bytes = b""
        fragment: bytes = b""
        while True:
            fragment = self.rfile.readline()
            if fragment:
                logging.debug(
                    "Recieved fragment %s from %s", fragment, self.client_address
                )
                request = request + fragment
            else:
                break

        logging.info("Recieved %s from %s", request, self.client_address)

        return request

    def __handle_request(self, request: bytes) -> None:
        protocols = Protocols()
        protocol_response: ProtocolResponse | None = protocols.parse_request(request)
        response: bytes | None
        match protocol_response.request_type:
            case "client":
                response = self._handle_client_request(protocol_response)
            case "server":
                response = self._handle_server_request(protocol_response)
            case "any":
                response = self._handle_generic_request(protocol_response)
            case _:
                response = None

        if response:
            self._send_response(response)

    def _send_response(self, response: bytes) -> None:
        logging.debug("Sending %s to %s", response, self.client_address)
        self.wfile.write(response)

    def _handle_client_request(self, request: ProtocolResponse) -> bytes:
        logging.debug("Header belongs to client")

        processed_server_list: list[bytes] = [
            self._pack_address(server.address)
            for server in self.storage.get_servers(request.game)
        ]

        return self._create_response(processed_server_list, request.response)

    def _handle_server_request(self, request: ProtocolResponse) -> bytes | None:
        logging.debug("Header belongs to server")
        address, port = self.client_address
        self.storage.update_server(
            Server(
                address=":".join([address, str(port)]),
                game=request.game,
                active=request.active,
                details=request.details,
                players=request.players,
            )
        )

        return request.response

    @staticmethod
    def _handle_generic_request(request: ProtocolResponse) -> bytes | None:
        logging.debug("Header could belong to anything")
        return request.response

    @staticmethod
    def _create_response(
        response: list[bytes],
        header: bytes | None = None,
        separator: bytes = b"",
    ) -> bytes:
        if header:
            response[0] = header + response[0]

        return separator.join(response)

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
