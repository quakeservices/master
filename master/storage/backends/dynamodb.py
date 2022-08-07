import logging
import os
from decimal import Decimal
from typing import Any, Mapping, Optional, Sequence, Union

from boto3.dynamodb.conditions import Attr
from boto3.session import Session
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table
from mypy_boto3_dynamodb.type_defs import (
    GetItemOutputTableTypeDef,
    PutItemOutputTableTypeDef,
    ScanOutputTableTypeDef,
    UpdateItemOutputTableTypeDef,
)

from master.constants import APP_NAME, DEFAULT_REGION, DEPLOYMENT_ENVIRONMENT
from master.storage import BaseStorage
from master.storage.models.server import Server

Item = dict[
    str,
    Union[
        bytes,
        bytearray,
        str,
        int,
        Decimal,
        bool,
        set[int],
        set[Decimal],
        set[str],
        set[bytes],
        set[bytearray],
        Sequence[Any],
        Mapping[str, Any],
        None,
    ],
]

DEFAULT_SESSION = Session()
DEFAULT_TABLE_NAME = f"{APP_NAME}-{DEPLOYMENT_ENVIRONMENT}"


class DynamoDbStorage(BaseStorage):
    table: Table
    dynamodb: DynamoDBServiceResource
    primary_key: str = "address"

    def __init__(
        self,
        table_name: str = DEFAULT_TABLE_NAME,
        region: str = DEFAULT_REGION,
        session: Optional[Session] = DEFAULT_SESSION,
    ):
        _session = session
        self.table = self._create_service_resource(table_name, region, _session)

    def _create_service_resource(
        self, table_name: str, region: str, session: Session
    ) -> Table:
        if DEPLOYMENT_ENVIRONMENT == "dev":
            # We're in development so use dynamodb-local
            self.dynamodb = session.resource(
                "dynamodb",
                region_name=region,
                endpoint_url="http://dynamodb-local:8000",
            )
        else:
            # We're in production or (unit) testing so use real endpoint
            # dynamodb client will be mocked out in unit testing
            self.dynamodb = session.resource("dynamodb", region_name=region)

        return self.dynamodb.Table(table_name)

    def initialise(self, table_name: str = APP_NAME) -> None:
        if DEPLOYMENT_ENVIRONMENT == "dev":
            self._create_table(table_name)

    def _create_table(self, table_name: str) -> None:
        logging.debug(f"Creating table {table_name}")
        try:
            self.dynamodb.create_table(
                TableName=table_name,
                BillingMode="PAY_PER_REQUEST",
                KeySchema=[
                    {"AttributeName": self.primary_key, "KeyType": "HASH"},
                ],
                AttributeDefinitions=[
                    {"AttributeName": self.primary_key, "AttributeType": "S"},
                ],
            )
        except self.dynamodb.meta.client.exceptions.ResourceInUseException:
            logging.debug("Table already exists, skipping creation.")

    def create_server(self, server: Server) -> bool:
        return self.update_server(server)

    def get_server(self, address: str, game: Optional[str] = None) -> Optional[Server]:
        server: Optional[Server] = None
        result = self._get_item(address)

        if result:
            server = Server.parse_obj(result)

        return server

    def _get_item(self, address: str) -> Item:
        response: GetItemOutputTableTypeDef = self.table.get_item(
            Key={"address": address}
        )
        item = response["Item"]
        return item

    def get_servers(self, game: Optional[str] = None) -> list[Server]:
        servers: list = []

        result = self._scan(game)
        for server in result:
            servers.append(Server.parse_obj(server))

        return servers

    def _scan(self, game: Optional[str]) -> list[Item]:
        response: ScanOutputTableTypeDef
        if game:
            response = self.table.scan(
                FilterExpression=Attr("game").eq(game) & Attr("active").eq(True)
            )
        else:
            response = self.table.scan(FilterExpression=Attr("active").eq(True))

        items = response["Items"]
        return items

    def update_server(self, server: Server) -> bool:
        return self._update_item(server)

    def _update_item(self, server: Server) -> bool:
        update_expression: str = "SET active=:a, game=:g, details=:d, players=:p"
        expression_attribute_values: dict[str, Any] = {
            ":a": server.active,
            ":g": server.game,
            ":d": server.details,
            ":p": server.players,
        }
        result: UpdateItemOutputTableTypeDef = self.table.update_item(
            Key={self.primary_key: server.address},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="UPDATED_NEW",
        )

        # The Attributes map is only present if ReturnValues was specified as
        # something other than NONE in the request.
        if "Attributes" in result:
            return True

        return False
