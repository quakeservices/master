import yaml
import os
import binascii

# TODO: Store in Hex, use binascii.hexlify/binasxii.unhexlify

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
        self.headers = headers.get('headers')
        for k, v in self.headers.items():
          try:
            self.headers[k] = binascii.unhexlify(v)
          except:
            self.headers[k] = v

   
    def __repr__(self):
        return self.game_name

    @property
    def name(self):
        return self.game_name

    def match_headers(self, header):
        for k, v in self.headers.items():
            if v.startswith(header):
                return True

        return False
