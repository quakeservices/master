import logging
import struct
from ipaddress import ip_address

from gameserver import GameServer

from aws_xray_sdk.core import xray_recorder


class MasterServer:
    def __init__(self, storage, protocols):
        logging.debug(f"{self.__class__.__name__ } - Initialising master server.")
        self.transport = None
        self.storage = storage
        self.protocols = protocols

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, address):
        response = None
        logging.debug(f"{self.__class__.__name__ } - Recieved {data} from {address}")
        xray_recorder.begin_segment('datagram_recieved')
        result = self.protocols.parse_data(data)

        if result.get('class') == 'B2M':
            response = self.handle_client(result)
        elif result.get('class') == 'S2M':
            response = self.handle_server(result, address)
        else:
            pass

        if response:
            logging.debug(f"{self.__class__.__name__ } - Sending {response} to {address}")
            self.transport.sendto(response, address)
        xray_recorder.end_segment()

    def handle_client(self, result):
        logging.debug(f"{self.__class__.__name__ } - Header belongs to client")
        response_header = result.get('resp', None)
        server_list = self.storage.list_server_addresses(result.get('game'))
        processed_server_list = [self.pack_address(_) for _ in server_list]
        return self.create_response(response_header, processed_server_list)

    def handle_server(self, result, address):
        logging.debug(f"{self.__class__.__name__ } - Header belongs to server")
        server = GameServer(address, result)
        if self.storage.get_server(server):
            self.storage.update_server(server)
        else:
            self.storage.create_server(server)

        if not server.active:
            self.storage.server_shutdown(server)

        return result.get('resp', None)

    @staticmethod
    def create_response(header, response):
        seperator = b''
        if header:
            response.insert(0, header)

        return seperator.join(response)

    @staticmethod
    def pack_address(address):
        """
        Takes string formatted address;
        eg, '192.168.0.1:27910'
        Converts to 6 byte binary string.
        H = unsigned short
        """
        port_format = '>H'
        ip, port = address.split(':')
        ip = ip_address(ip).packed
        port = struct.pack(port_format, int(port))
        return ip + port
