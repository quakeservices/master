import re
from typing import Optional, Union


def dictify_players(data: list[bytes], encoding: str) -> list[Optional[dict[str, str]]]:
    """
    Convert a list of bytes into a list of dicts if they match regex
    """
    players: list[Optional[dict[str, str]]] = []
    player_regex = re.compile(
        r'(?P<score>-?\d+) (?P<ping>\d+) (?P<name>".+")', flags=re.ASCII
    )
    for player in data:
        player_re = re.match(player_regex, player.decode(encoding))
        if player_re:
            players.append(player_re.groupdict())

    return players


def dictify_status(
    data: bytes, encoding: str, split: str, max_length: int = 128
) -> dict:
    """
    Convert a byte string into a dict
    Also convert strings to integers if possible
    """
    decoded_status: str = data.decode(encoding)

    # Split status on `split` and remove any blank strings
    # TODO: Validate whether server can send empty values
    list_status: list[str] = [_ for _ in decoded_status.split(split) if _]

    # If the length of status isn't even, truncate the last value
    if len(list_status) % 2 != 0:
        list_status = list_status[:-1]

    # Coalesce list into key:value pairs
    # ['a', 1, 'b', 2]
    # turns into
    # {'a': 1, 'b': 2}
    zip_status = zip(list_status[0::2], list_status[1::2])

    # For each key:value;
    # Truncate if it's longer than 128 characters
    # Coalesce strings into integers if possible
    status: dict[str, Union[str, int]] = {}
    for status_k, status_v in zip_status:
        if len(status_v) > max_length:
            status_v = status_v[:max_length]

        try:
            status[status_k] = int(status_v)
        except ValueError:
            status[status_k] = status_v

    return status
