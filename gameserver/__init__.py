import logging
import re
import json
import os
import sys
from typing import Tuple, NoReturn

import geoip2.database


geoip_db = 'nonfree/GeoIP.dat'
if os.path.isfile(geoip_db):
    reader = geoip2.database.Reader(geoip_db)
else:
    print(f"Could not find {geoip_db}")
    sys.exit(1)


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

    def __init__(self,
                 address: Tuple[str, int],
                 result):
        self.server_address = address
        self.game = 'quake2'
        self.result = result
        self.country = self.get_country()
        self.players = list()
        self.status = dict()
        if result.get('status'):
            self.dictify_status(result.get('status')[0])
            self.dictify_players(result.get('status')[1:])
        self.player_count = len(self.players)
        self.players = json.dumps(self.players)
        self.status = json.dumps(self.status)

    @property
    def ip(self) -> str: # pylint: disable=invalid-name
        return self.server_address[0]

    @property
    def port(self) -> int:
        return self.server_address[1]

    @property
    def address(self) -> str:
        return ':'.join([self.ip, str(self.port)])

    @property
    def encoding(self) -> str:
        return self.result.get('encoding')

    @property
    def active(self) -> bool:
        return self.result.get('active')

    def get_country(self) -> str:
        """
        Returns two letter country code for a particular IP
        If none exists then ZZ is returned as unknown.
        """
        result = 'ZZ'
        try:
            result = reader.city(self.ip).country.iso_code
        except geoip2.errors.AddressNotFoundError:
            pass

        return result

    def dictify_players(self, data: str) -> NoReturn:
        player_regex = re.compile(r'(?P<score>-?\d+) (?P<ping>\d+) (?P<name>".+")', flags=re.ASCII)
        for player in data:
            player = re.match(player_regex, player.decode(self.encoding))
            if player:
                self.players.append(player.groupdict())

    def dictify_status(self, data: str) -> NoReturn:
        split_on = self.result.get('split_on', '\\')

        if data:
            str_status = data.decode(self.encoding)
            list_status = str_status.split(split_on)[1:]
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
