from typing import Literal, Union

Record = dict[Literal["key", "values"], Union[str, list[str]]]
Records = dict[str, dict[Literal["TXT", "CNAME", "A"], list[Record]]]
