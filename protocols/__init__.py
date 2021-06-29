import os
import logging
import yaml
from typing import List, NoReturn

from .proxy import ProxyProtocol

# Request = namedtuple('Request', 'header', 'status', 'players')


class Protocols:
    def __init__(self, header_order="master"):
        logging.debug(f"{self.__class__.__name__ } - Initialising protocols.")
        if header_order == "server":
            self.header_order = ["B2M", "S2M"]
        elif header_order == "client":
            self.header_order = ["B2M", "S2M"]
        else:
            self.header_order = ["B2M", "S2M"]

        self.protocols = list()
        self.load_protocols()

    @staticmethod
    def gather_protocol_files() -> List[str]:
        config_files = []
        module_path = os.path.abspath(os.path.dirname(__file__))
        config_path = os.path.join(module_path, "config")
        for _ in os.listdir(config_path):
            if _.endswith(".yml"):
                config_files.append(os.path.join(config_path, _))

        return config_files

    def load_protocols(self) -> NoReturn:
        logging.debug(f"{self.__class__.__name__ } - Loading protocols...")
        for config_file in self.gather_protocol_files():
            self.load_protocol(config_file)

    def load_protocol(self, config_file: str) -> NoReturn:
        logging.debug(f"{self.__class__.__name__ } - Reading {config_file}")
        with open(config_file, "rb") as config_file_handle:
            config = yaml.load(config_file_handle, Loader=yaml.FullLoader)
            if config.get("active", False):
                self.protocols.append(GameProtocol(config))
                logging.debug(f"{self.__class__.__name__ } - Loaded {config}")

    def find_protocol(self, header: str):
        for game in self.protocols:
            result = game.match_header(self.header_order, header)
            if result:
                return {
                    "game": game.name,
                    "resp": result.get("resp", None),
                    "encoding": game.encoding,
                    "active": result.get("active", True),
                    "class": result.get("class", self.header_order[0]),
                }

        return False

    def parse_data(self, data):
        logging.debug(f"{self.__class__.__name__ } - Parsing {data}")
        if len(data) >= 16:
            sanitised_data = ProxyProtocol.parse_data(data)
        else:
            sanitised_data = data
        logging.debug(f"{self.__class__.__name__ } - Sanitised as {sanitised_data}")
        header, *status = sanitised_data.splitlines()
        logging.debug(f"{self.__class__.__name__ } - Header is {header}")
        result = self.find_protocol(header)
        if result:
            result["header"] = header
            result["status"] = status
            return result
        else:
            return False


class GameProtocol:
    def __init__(self, protocol):
        self.protocol = protocol
        logging.debug(
            f"{self.__class__.__name__ } - Initialising protocols for {self.name}"
        )
        self.process_headers()

    def __repr__(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        return self.protocol.get("game", "Unknown")

    @property
    def encoding(self) -> str:
        return self.protocol.get("encoding", "latin1")

    def match_header(self, header_order: str, header: bytes):
        for header_class in [_ for _ in header_order if _ in self.protocol.keys()]:
            for k, v in self.protocol[
                header_class
            ].items():  # pylint: disable=invalid-name
                if v.get("recv", "").startswith(header):
                    v["class"] = header_class
                    if k == "shutdown":
                        v["active"] = False

                    return v

        return False

    def process_headers(self) -> NoReturn:
        for header_class in ["S2M", "B2M"]:
            for k, v in self.protocol[
                header_class
            ].items():  # pylint: disable=invalid-name
                self.protocol[header_class][k] = self.encode_headers(v)

    def encode_headers(self, headers):
        for _ in ["recv", "resp"]:
            if _ in headers:
                headers[_] = self.encoder(headers[_])
        return headers

    def encoder(self, data: str) -> bytes:
        return bytes(data, self.encoding, errors="backslashreplace")
