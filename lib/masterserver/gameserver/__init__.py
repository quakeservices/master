import json
import re


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

    game: str = "quake2"
    players: list = []
    player_count: int = 0
    status: dict = {}

    def __init__(self, address: tuple[str, int], result: dict):
        self.server_address: tuple[str, int] = address
        self.result: dict = result

        if result.get("status"):
            self.dictify_status(result.get("status")[0])
            self.dictify_players(result.get("status")[1:])

        self.player_count = len(self.players)

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

    def dictify_players(self, data: bytes):
        player_regex = re.compile(
            r'(?P<score>-?\d+) (?P<ping>\d+) (?P<name>".+")', flags=re.ASCII
        )
        for player in data:
            player = re.match(player_regex, player.decode(self.encoding))
            if player:
                self.players.append(player.groupdict())

    def dictify_status(self, data: bytes, split_on: str = "\\"):
        decoded_status: str = data.decode(self.encoding)
        list_status: list = decoded_status.split(split_on)[1:]

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
