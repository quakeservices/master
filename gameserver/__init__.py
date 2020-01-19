import logging
import re
import json
import os
import sys

import geoip2.database


# TODO: Add logging around this instead of silently failing
# TODO: Make less garbage
try:
    reader = geoip2.database.Reader('/usr/share/GeoIP/GeoIP.dat')
except:
    try:
        reader = geoip2.database.Reader('./nonfree/GeoIP.dat')
    except:
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

    def __init__(self, address, result):
        self.server_address = address
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
    def ip(self): # pylint: disable=invalid-name
        return self.server_address[0]

    @property
    def port(self):
        return self.server_address[1]

    @property
    def address(self):
        return ':'.join([self.ip, str(self.port)])

    @property
    def encoding(self):
        return self.result.get('encoding')

    @property
    def active(self):
        return self.result.get('active')

    def get_country(self):
        """
        Returns two letter country code for a particular IP
        If none exists then ZZ is returned as unknown.
        """
        try:
            result = reader.city(self.ip).country.iso_code
        except geoip2.errors.AddressNotFoundError:
            pass

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
        # TODO: Investigate replacing this with Construct
        #       At the very least look at struct

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
