from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module


class Server(BaseModel):
    class Config:
        str_strip_whitespace = True

    address: str = Field(
        description="Colon separated tuple of the server IP address and port, e.g.: <IP>:<PORT>"
    )
    active: bool = Field(
        description="Whether the server is active or if a shutdown request was recieved",
        default=False,
    )
    game: str = Field(description="Name of the game")
    details: dict = Field(description="Server details", default_factory=dict)
    players: list = Field(description="Player details", default_factory=list)
