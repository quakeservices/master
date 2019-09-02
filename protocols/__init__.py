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
                      'encoding': game.encoding}

        return False

    def is_server(self, header):
        result = self.find_protocol('server', header)
        return result

    def is_client(self, header):
        result = self.find_protocol('client', header)
        return result


class GameProtocol(object):
    def __init__(self, protocols):
        self.protocols = protocols
        self.game_name = protocols.get('game')
        self.game_engine = protocols.get('engine', None)
        self.game_encoding = protocols.get('encoding', None) 
        logging.debug(f"{__class__.__name__ } - Initialising protocols for {self.game_name}")

    def __repr__(self):
        return self.game_name

    @property
    def name(self):
        return self.game_name

    @property
    def encoding(self):
        return self.game_encoding

    def match_header(self, category, header):
        if self.protocols.get(category, False):
            for k, v in self.protocols[category].items():
                if v.get('recv', '').startswith(header):
                    return v

        return False
