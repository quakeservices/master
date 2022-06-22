import os
from dataclasses import dataclass
from typing import Optional

import yaml
from helpers import LoggingMixin

from protocols.models import GameProtocol, GameProtocolResponse
from protocols.proxy import ProxyProtocol


class GameProtocols(LoggingMixin):
    protocols: list[GameProtocol] = []

    def __init__(self):
        self.log("Initialising protocols.")
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
        self.log("Loading protocols...")
        for config_file in self._gather_protocol_files():
            self._load_protocol(config_file)

    def _load_protocol(self, config_file: str):
        self.log(f"Reading {config_file}")
        with open(config_file, "rb") as config_file_handle:
            config = yaml.safe_load(config_file_handle)
            if config.get("active", False):
                self.protocols.append(GameProtocol(**config))
                self.log(f"Loaded {config}")

    def _find_protocol(self, header: bytes) -> GameProtocolResponse:
        response: GameProtocolResponse = GameProtocolResponse()

        for game in self.protocols:
            response = game.match_receive_header(header)
            if response.header_match:
                break

        return response

    def parse_request(self, request: bytes) -> GameProtocolResponse:
        self.log(f"Parsing {request!r}")
        parsed_request: bytes
        if len(request) >= 16:
            parsed_request = ProxyProtocol.parse_request(request)
        else:
            parsed_request = request

        self.log(f"Sanitised as {parsed_request!r}")
        header, *status = parsed_request.splitlines()

        self.log(f"Header is {header!r}")
        response: GameProtocolResponse = self._find_protocol(header)

        if response.header_match:
            response.header = header
            response.status = status

        return response
