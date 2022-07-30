import json
import os

import click
from pydantic import schema_json_of

from master.protocols.models.game import GameProtocol
from master.protocols.models.response import ProtocolResponse

schema_path: str = "docs/schemas"
schemas: list[dict] = [
    {
        "title": "GameProtocol schema",
        "model": GameProtocol,
        "filename": "game_protocol.json",
    },
    {
        "title": "ProtocolResponse schema",
        "model": ProtocolResponse,
        "filename": "protocol_response.json",
    },
]


@click.group()
def schema_cli() -> None:
    pass


@schema_cli.group()
def schema() -> None:
    """
    Schema operations
    """


@schema.command()
def dump() -> None:
    for schema_ref in schemas:
        path: str = os.path.join(schema_path, schema_ref["filename"])

        with open(path, "w", encoding="utf-8") as handle:
            try:
                click.echo(f"Dumping {schema_ref['model']}")
                handle.write(
                    schema_json_of(
                        schema_ref["model"], title=schema_ref["title"], indent=2
                    )
                )
            except TypeError:
                pass

    click.echo("Done")
