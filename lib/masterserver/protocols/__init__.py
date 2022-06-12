import logging
import os
from dataclasses import dataclass
from typing import Optional

import yaml

from .game_protocol import GameProtocol, GameProtocolResponse
from .proxy import ProxyProtocol


@dataclass
class ProtocolResponse:
    found_header: bool = False
    game: Optional[str] = None
    response: Optional[bytes] = None
    active: bool = False
    encoding: str = "latin1"
    header: Optional[str] = None
    status: Optional[str] = None
    header_source: Optional[str] = None
    header_type: Optional[str] = None


class Protocols:
    protocols: list[GameProtocol] = []

    def __init__(self):
        logging.debug(f"{self.__class__.__name__ } - Initialising protocols.")
        self.load_protocols()

    @staticmethod
    def _gather_protocol_files() -> list[str]:
        config_files: list[str] = []
        config_path: str = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "config")
        )
        for filename in os.listdir(config_path):
            if filename.endswith(".yml"):
                config_files.append(os.path.join(config_path, filename))

        return config_files

    def load_protocols(self):
        logging.debug(f"{self.__class__.__name__ } - Loading protocols...")
        for config_file in self._gather_protocol_files():
            self._load_protocol(config_file)

    def _load_protocol(self, config_file: str):
        logging.debug(f"{self.__class__.__name__ } - Reading {config_file}")
        with open(config_file, "rb") as config_file_handle:
            config = yaml.safe_load(config_file_handle)
            if config.get("active", False):
                self.protocols.append(GameProtocol(**config))
                logging.debug(f"{self.__class__.__name__ } - Loaded {config}")

    def _find_protocol(self, header: bytes) -> ProtocolResponse:
        game_protocol: Optional[GameProtocolResponse] = None
        response: ProtocolResponse = ProtocolResponse()

        for game in self.protocols:
            game_protocol = game.match_receive_header(header)
            if game_protocol.header_match:
                response = ProtocolResponse(
                    game=game_protocol.game,
                    response=game_protocol.response,
                    encoding=game_protocol.encoding,
                    active=game_protocol.active,
                    found_header=True,
                    header_type=game_protocol.header_type,
                )
                break

        return response

    def parse_request(self, request: bytes) -> ProtocolResponse:
        logging.debug(f"{self.__class__.__name__ } - Parsing {request}")
        parsed_request: bytes
        if len(request) >= 16:
            parsed_request = ProxyProtocol.parse_request(request)
        else:
            parsed_request = request

        logging.debug(f"{self.__class__.__name__ } - Sanitised as {parsed_request}")
        header, *status = parsed_request.splitlines()

        logging.debug(f"{self.__class__.__name__ } - Header is {header}")
        response: ProtocolResponse = self._find_protocol(header)

        if response.found_header:
            response.header = header
            response.status = status

        return response
