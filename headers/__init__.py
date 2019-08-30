import yaml
import os
import logging


class Headers(object):
    def __init__(self):
        logging.debug(f"{__class__.__name__ } - Initialising headers.")
        self.headers = self.load_headers()

    def gather_header_files(self):
        logging.debug(f"{__class__.__name__ } - Gathering headers...")
        config_files = []
        module_path = os.path.abspath(os.path.dirname(__file__))
        config_path = os.path.join(module_path, 'config')
        for _ in os.listdir(config_path):
            if _.endswith('.yml'):
                config_files.append(os.path.join(config_path, _))

        return config_files

    def load_headers(self):
        logging.debug(f"{__class__.__name__ } - Loading headers...")
        headers = []
        for config_file in self.gather_header_files():
            with open(config_file, 'rb') as config_file_handle:
                config = yaml.load(config_file_handle, Loader=yaml.FullLoader)
                if config.get('active', False):
                    headers.append(GameHeaders(config))
                    logging.debug(f"{__class__.__name__ } - Loaded {config}")

        return headers

    def find_header(self, category, header):
        for game in self.headers:
            result = game.match_header(category, header)
            if result:
                return (game.name, result)

        return False

    def is_server(self, header):
        result = self.find_header('server', header)
        return result

    def is_client(self, header):
        result = self.find_header('client', header)
        return result


class GameHeaders(object):
    def __init__(self, headers):
        self.headers = headers
        self.game_name = self.headers.get('game')
        self.game_engine = self.headers.get('engine', None)
        logging.debug(f"{__class__.__name__ } - Initialising headers for {self.game_name}")
   
    def __repr__(self):
        return self.game_name

    @property
    def name(self):
        return self.game_name

    def match_header(self, category, header):
        if self.headers.get(category, None):
            for k, v in self.headers[category].items():
                if v.get('resv', '').startswith(header):
                    return v

        return False
