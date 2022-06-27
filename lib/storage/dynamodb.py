from dataclasses import fields
from typing import Any, Optional

import boto3
from boto3.dynamodb.conditions import Attr, Key
from constants import APP_NAME
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table
from mypy_boto3_dynamodb.type_defs import (GetItemOutputTableTypeDef,
                                           PutItemOutputTableTypeDef,
                                           ScanOutputTableTypeDef,
                                           UpdateItemOutputTableTypeDef)

from . import BaseStorage, Server


class DynamoDbStorage(BaseStorage):
    table: Table

    def __init__(self, table_name: str = APP_NAME):
        session = boto3.session.Session()
        dynamodb: DynamoDBServiceResource = session.resource("dynamodb")
        self.table: Table = dynamodb.Table(table_name)

    def create_server(self, server_data: Server) -> bool:
        result: bool = self._put_item(server_data)
        return result

    def _put_item(self, server_data: Server) -> bool:
        result: PutItemOutputTableTypeDef = self.table.put_item(
            Item={
                "server": server_data.server_address,
                "active": server_data.active,
                "game": server_data.game,
                "details": server_data.details,
                "players": server_data.players,
            }
        )

        if result:
            return True

        return False

    def get_server(
        self, server_address: str, game: Optional[str] = None
    ) -> Optional[Server]:
        server: Optional[Server] = None
        result = self._get_item(server_address)

        if result:
            server = Server(**result)

        return server

    def _get_item(self, server_address: str):
        response: GetItemOutputTableTypeDef = self.table.get_item(
            Key={"server_address": server_address}
        )
        item: GetItemOutputTableTypeDef.Item = response["Item"]
        return item

    def get_servers(self, game: Optional[str] = None) -> list[Server]:
        servers: list = []

        result = self._scan(game)
        for server in result:
            servers.append(Server(**server))

        return servers

    def _scan(self, game: Optional[str]):
        response: ScanOutputTableTypeDef
        if game:
            response = self.table.scan(
                FilterExpression=Attr("game").eq(game) & Attr("active").eq(True)
            )
        else:
            response = self.table.scan(FilterExpression=Attr("active").eq(True))

        items = response["Items"]
        return items

    def update_server(self, server_data: Server) -> bool:
        result: bool = self._update_item(server_data)
        return result

    def _update_item(self, server_data: Server) -> bool:
        update_expression: str = "SET active=:a, game=:g, details=:d, players=:p"
        expression_attribute_values: dict[str, Any] = {
            ":a": server_data.active,
            ":g": server_data.game,
            ":d": server_data.details,
            ":p": server_data.players,
        }
        result: UpdateItemOutputTableTypeDef = self.table.update_item(
            Key={"server_address": server_data.server_address},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnedValues="UPDATED_NEW",
        )

        # The Attributes map is only present if ReturnValues was specified as
        # something other than NONE in the request.
        if "Attributes" in result:
            return True

        return False
