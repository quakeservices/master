import re
import json
from typing import Tuple, NoReturn, Dict, List

# import geoip2.database

# geoip_db = 'nonfree/GeoIP.dat'
# if os.path.isfile(geoip_db):
#     reader = geoip2.database.Reader(geoip_db)
# else:
#     print(f"Could not find {geoip_db}")
#     sys.exit(1)


class GameServer:
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

    def __init__(self, address: Tuple[str, int], result: Dict):
        self.server_address: Tuple[str, int] = address
        self.game: str = "quake2"
        self.result: Dict = result
        self.country = self.get_country()
        self.players = list()
        self.status = dict()
        if result.get("status"):
            self.dictify_status(result.get("status")[0])
            self.dictify_players(result.get("status")[1:])
        self.player_count: int = len(self.players)

    @property
    def ip(self) -> str:  # pylint: disable=invalid-name
        return self.server_address[0]

    @property
    def port(self) -> int:
        return self.server_address[1]

    @property
    def address(self) -> str:
        return ":".join([self.ip, str(self.port)])

    @property
    def encoding(self) -> str:
        return self.result.get("encoding")

    @property
    def split_on(self) -> str:
        return self.result.get("split_on")

    @property
    def active(self) -> bool:
        return self.result.get("active")

    @property
    def json_status(self) -> str:
        return json.dumps(self.status)

    @property
    def json_players(self) -> str:
        return json.dumps(self.players)

    def get_country(self) -> str:
        """
        Returns two letter country code for a particular IP
        If none exists then ZZ is returned as unknown.
        TODO: Fix this
        """
        result = "ZZ"
        # try:
        #    result = reader.city(self.ip).country.iso_code
        # except geoip2.errors.AddressNotFoundError:
        #    pass

        return result

    def dictify_players(self, data: bytes) -> NoReturn:
        player_regex = re.compile(
            r'(?P<score>-?\d+) (?P<ping>\d+) (?P<name>".+")', flags=re.ASCII
        )
        for player in data:
            player = re.match(player_regex, player.decode(self.encoding))
            if player:
                self.players.append(player.groupdict())

    def dictify_status(self, data: bytes, split_on: str = "\\") -> NoReturn:
        decoded_status: str = data.decode(self.encoding)
        list_status: List = decoded_status.split(split_on)[1:]

        """
        If the length of status isn't even, truncate the last value
        """
        if len(list_status) % 2 != 0:
            list_status = list_status[:-1]

        """
        Coalesce list into key:value pairs
        ['a', 1, 'b', 2]
        turns into
        {'a': 1, 'b': 2}
        """
        zip_status = zip(list_status[0::2], list_status[1::2])

        """
        For each key:value;
        Truncate if it's longer than 128 characters
        Coalesce strings into integers if possible
        """
        for status_k, status_v in zip_status:
            if len(status_v) > 128:
                status_v = status_v[:128]

            try:
                self.status[status_k] = int(status_v)
            except ValueError:
                self.status[status_k] = status_v
