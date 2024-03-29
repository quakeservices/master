import os

import click
from pydantic import schema_json_of  # pylint: disable=no-name-in-module

from master.protocols.models.game import GameProtocol
from master.protocols.models.response import ProtocolResponse

# json_schema_for_humans isn't part of the `master` build and doesn't need to be
# if we can't load it we're probably not meant to
try:
    import json_schema_for_humans as jsfh  # mypy: ignore

    JSFH_AVAILABLE = True
except (ModuleNotFoundError, ImportError):
    click.echo("Unable to load json_schema_for_humans, skipping...")
    JSFH_AVAILABLE = False

schema_path: str = "docs/schemas"
schemas: list[dict] = [
    {
        "title": "GameProtocol schema",
        "model": GameProtocol,
        "filename": "game_protocol",
    },
    {
        "title": "ProtocolResponse schema",
        "model": ProtocolResponse,
        "filename": "protocol_response",
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
    click.echo("Dumping schemas")
    for schema_ref in schemas:
        path: str = os.path.join(schema_path, schema_ref["filename"] + ".json")

        with open(path, "w", encoding="utf-8") as handle:
            schema_string: str = schema_json_of(
                schema_ref["model"], title=schema_ref["title"], indent=2
            )
            handle.write(schema_string)

    click.echo("Done")


@schema.command()
def generate() -> None:
    if not JSFH_AVAILABLE:
        return None

    config = jsfh.GenerationConfiguration(
        copy_css=False, copy_js=False, expand_buttons=True, template_name="md"
    )

    click.echo("Generating schema documentation")
    for schema_ref in schemas:
        path_md: str = os.path.join(schema_path, schema_ref["filename"] + ".md")
        path_json: str = os.path.join(schema_path, schema_ref["filename"] + ".json")

        with open(path_json, "r", encoding="utf-8") as handle_json, open(
            path_md, "w", encoding="utf-8"
        ) as handle_md:
            jsfh.generate_from_file_object(
                schema_file=handle_json, result_file=handle_md, config=config
            )

    click.echo("Done")
    return None
