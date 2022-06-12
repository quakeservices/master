import asyncio
import logging
import struct
from ipaddress import ip_address
from typing import Optional

from gameserver import GameServer
from protocols import ProtocolResponse, Protocols
from storage import PynamoDbStorage


class MasterServer(asyncio.DatagramProtocol):
    seperator: bytes = b""
    port_format: str = ">H"  # Unsigned short
    transport: asyncio.DatagramTransport

    def __init__(self):
        logging.debug(f"{self.__class__.__name__ } - Initialising master server.")
        self.storage = PynamoDbStorage()
        self.protocols = Protocols()

    def connection_made(self, transport: asyncio.DatagramTransport):
        self.transport = transport

    def datagram_received(self, data: bytes, address: tuple[str, int]):
        logging.debug(f"{self.__class__.__name__ } - Recieved {data} from {address}")

        response: Optional[bytes] = None
        protocol_response: ProtocolResponse = self.protocols.parse_request(data)

        if protocol_response.found_header:
            if protocol_response.header_type == "client":
                response = self._handle_client(protocol_response)
            elif (
                protocol_response.header_type == "server"
                or protocol_response.header_type == "any"
            ):
                response = self._handle_server(protocol_response, address)

            if response:
                self._send_response(response, address)

    def _send_response(self, response: bytes, address: tuple[str, int]):
        logging.debug(f"{self.__class__.__name__ } - Sending {response} to {address}")
        self.transport.sendto(response, address)

    def _handle_client(self, request: ProtocolResponse) -> bytes:
        logging.debug(f"{self.__class__.__name__ } - Header belongs to client")

        response_header = request.response
        server_list = self.storage.list_server_addresses(request.game)
        processed_server_list = [self._pack_address(server) for server in server_list]
        return self._create_response(response_header, processed_server_list)

    def _handle_server(
        self, request: ProtocolResponse, address: tuple[str, int]
    ) -> Optional[bytes]:
        logging.debug(f"{self.__class__.__name__ } - Header belongs to server")
        server = GameServer(address, request)
        if server.active:
            self.storage.save_server(server)
        else:
            self.storage.server_shutdown(server)

        return request.response

    def _create_response(self, header: bytes, response: list[bytes]) -> bytes:
        if header:
            response.insert(0, header)

        return self.seperator.join(response)

    def _pack_address(self, address: str) -> bytes:
        """
        Takes string formatted address;
        eg, '192.168.0.1:27910'
        Converts to 6 byte binary string.
        """
        server_ip: str
        server_port: str

        server_ip, server_port = address.split(":")

        server_ip_bytes: bytes = ip_address(server_ip).packed
        server_port_bytes: bytes = struct.pack(self.port_format, int(server_port))

        return server_ip_bytes + server_port_bytes
