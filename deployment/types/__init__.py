from typing import Literal

Record = dict[Literal["name", "targets"], str | list[str]]
Records = dict[str, dict[Literal["TXT", "CNAME", "A"], list[Record]]]
