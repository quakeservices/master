import logging
import re
import json

import GeoIP

# TODO: Where is this in scope?
GI = GeoIP.new(GeoIP.GEOIP_MEMORY_CACHE)

class GameServer():
    """
    Input:
        b'\\cheats\\0\\deathmatch\\1\\dmflags\\16\\fraglimit\\0'
    Split the above byte-string into list of strings resulting in:
        ['cheats', '0', 'deathmatch', '1', 'dmflags', '16', 'fraglimit', '0']
    If the number of keys/values isn't equal truncate the last value
    Zip the above list of strings and then convert zip object into a dict:
        {'cheats': 0, 'deathmatch': 1, 'dmflags': 16, 'fraglimit': 0]
    For each key/value try to convert it to an int ahead of time.

    At the end of the heartbeat is the player list split by \n
    Example: <score> <ping> <player>\n
    """

    def __init__(self, address, data, result):
        self.server_address = address
        self.result = result
        self.country = self.get_country()
        self.players = list()
        self.status = dict()
        if data:
            self.dictify_status(data[0])
            self.dictify_players(data[1:])
        self.player_count = len(self.players)
        self.players = json.dumps(self.players)
        self.status = json.dumps(self.status)

    def ip(self): # pylint: disable=invalid-name
        return self.server_address[0]

    def port(self):
        return self.server_address[1]

    def address(self):
        return ':'.join([self.ip, str(self.port)])

    def encoding(self):
        return self.result.get('encoding')

    def active(self):
        return self.result.get('active')

    def get_country(self):
        """
        Returns two letter country code for a particular IP
        If none exists then ZZ is returned as unknown.
        """
        result = GI.country_code_by_addr(self.ip)
        if result:
            return result

        return 'ZZ'

    def dictify_players(self, data):
        player_regex = re.compile(r'(?P<score>-?\d+) (?P<ping>\d+) (?P<name>".+")', flags=re.ASCII)
        for player in data:
            player = re.match(player_regex, player.decode(self.encoding))
            if player:
                self.players.append(player.groupdict())

    def dictify_status(self, data):
        # TODO: Assumes split on \\

        if data:
            str_status = data.decode(self.encoding)
            list_status = str_status.split('\\')[1:]
            if len(list_status) % 2 != 0:
                list_status = list_status[:-1]

            zip_status = zip(list_status[0::2], list_status[1::2])

            for status_k, status_v in zip_status:
                if len(status_v) > 128:
                    status_v = status_v[:128]

                try:
                    self.status[status_k] = int(status_v)
                except ValueError:
                    self.status[status_k] = status_v
