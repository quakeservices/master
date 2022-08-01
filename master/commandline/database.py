import socket
from pprint import pprint

import click
from boto3.session import Session

from master.constants import APP_NAME, DEFAULT_REGION

DEFAULT_HOST: str = socket.gethostbyname(socket.gethostname())
DEFAULT_PORT: int = 8000
AWS_ACCESS_KEY_ID: str = "DUMMYIDEXAMPLE"
AWS_SECRET_ACCESS_KEY: str = "DUMMYEXAMPLEKEY"


# TODO: Multiple backend support
#       Boto typing


@click.group()
def database_cli() -> None:
    pass


@database_cli.group()
def database() -> None:
    """
    Database operations
    """


@database.command()
def scan() -> None:
    session = Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=DEFAULT_REGION,
    )

    dynamodb = session.resource(
        "dynamodb",
        region_name=DEFAULT_REGION,
        endpoint_url=f"http://{DEFAULT_HOST}:{DEFAULT_PORT}",
    )
    table = dynamodb.Table(APP_NAME)
    pprint(table.scan())
