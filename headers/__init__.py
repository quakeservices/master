import yaml
import os

# TODO: Header object
#       Headers of header objects

class Headers(object):
    def __init__(self):
        self.headers = self.load_headers()

    def load_headers(self):
        headers = []
        module_path = os.path.abspath(os.path.dirname(__file__))
        config_path = os.path.join(module_path, 'config')
        config_files = [_ for _ in os.listdir(config_path) if _.endswith('.yml')]
        for config_file in config_files:
            config_file_path = os.path.join(config_path, config_file)
            with open(config_file_path, 'rb') as config_file_handle:
                config = yaml.load(config_file_handle, Loader=yaml.FullLoader)
                if config.get('active', False):
                    headers.append(GameHeaders(config))

        return headers

    def find_header(self, header):
        for game in self.headers:
            if game.match_byte_headers(header):
                return game.name

        return False

    def is_server(self, header):
        """
        Should these call a simplified find_header()?
        """
        for game in self.headers:
            if game.match_byte_headers(header):
                return True

        return False

    def is_client(self, header):
        """
        Should these call a simplified find_header()?
        """
        for game in self.headers:
            if game.match_byte_headers(header):
                return True

        return False


class GameHeaders(object):
    def __init__(self, headers):
        self.game_name = headers.get('game')
        self.str_headers = headers.get('headers')
        self.byte_headers = {}
        for k, v in self.str_headers.items():
            self.byte_headers[k] = v.encode('ascii')
   
    def __repr__(self):
        return self.game_name

    @property
    def name(self):
        return self.game_name

    def match_byte_headers(self, header):
        for k, v in self.byte_headers.items():
            print(v)
            if v.startswith(header):
                return True

        return False

    def match_str_headers(self, header):
        for k, v in self.str_headers.items():
            if v.startswith(header):
                return True

        return False
