import yaml
import os
import logging


class Protocols(object):
    def __init__(self):
        logging.debug(f"{__class__.__name__ } - Initialising protocols.")
        self.protocols = self.load_protocols()

    def gather_protocol_files(self):
        logging.debug(f"{__class__.__name__ } - Gathering protocols...")
        config_files = []
        module_path = os.path.abspath(os.path.dirname(__file__))
        config_path = os.path.join(module_path, 'config')
        for _ in os.listdir(config_path):
            if _.endswith('.yml'):
                config_files.append(os.path.join(config_path, _))

        return config_files

    def load_protocols(self):
        logging.debug(f"{__class__.__name__ } - Loading protocols...")
        protocols = []
        for config_file in self.gather_protocol_files():
            logging.debug(f"{__class__.__name__ } - Reading {config_file}")
            with open(config_file, 'rb') as config_file_handle:
                config = yaml.load(config_file_handle, Loader=yaml.FullLoader)
                if config.get('active', False):
                    protocols.append(GameProtocol(config))
                    logging.debug(f"{__class__.__name__ } - Loaded {config}")

        return protocols

    def find_protocol(self, category, header):
        for game in self.protocols:
            result = game.match_header(category, header)
            if result:
                return {'game': game.name,
                        'resp': result.get('resp', None),
                        'encoding': game.encoding,
                        'active': result.get('active', True)}

        return False

    def is_server(self, header):
        return self.find_protocol('server', header)

    def is_client(self, header):
        return self.find_protocol('client', header)


class GameProtocol(object):
    def __init__(self, protocol):
        self.protocol = protocol
        logging.debug(f"{__class__.__name__ } - Initialising protocols for {self.name}")
        self.process_headers()

    def __repr__(self):
        return self.name

    @property
    def name(self):
        return self.protocol.get('game', 'Unknown')

    @property
    def encoding(self):
        return self.protocol.get('encoding', 'latin1')

    def match_header(self, category, header):
        if self.protocol.get(category, False):
            for k, v in self.protocol[category].items():
                if v.get('recv', '').startswith(header):
                    if k == 'shutdown':
                        v['active'] = False

                    return v

        return False

    def process_headers(self):
        for category in ['server', 'client']:
            for k, v in self.protocol[category].items():
                self.protocol[category][k] = self.encode_headers(v)
    
    def encode_headers(self, headers):
        for _ in ['recv', 'resp']:
            if _ in headers:
                headers[_] = self.encoder(headers[_])
        return headers

    def encoder(self, data):
        return bytes(data, self.encoding, errors='backslashreplace')
